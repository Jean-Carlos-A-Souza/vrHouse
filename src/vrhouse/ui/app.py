"""Simple desktop UI to guide novice users through the conversion pipeline."""
from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from vrhouse.core import SceneSpecification
from vrhouse.pipeline.importers.multi_importer import iter_supported_suffixes
from vrhouse.pipeline.runner import run_conversion


class VRHouseApp(tk.Tk):
    """Tkinter based shell exposing the vrHouse pipeline to end users."""

    def __init__(self) -> None:
        super().__init__()
        self.title("vrHouse - Conversor VR")
        self.geometry("640x360")
        self.minsize(560, 320)

        self._queue: queue.Queue[tuple[float, str]] = queue.Queue()
        self._worker: Optional[threading.Thread] = None
        self._last_result: Optional[dict[str, object]] = None

        self._build_widgets()
        self._poll_updates()

    def _build_widgets(self) -> None:
        padding = {"padx": 12, "pady": 6}

        header = ttk.Label(
            self,
            text=(
                "Transforme suas plantas 3D em experiências VR realistas.\n"
                "Selecione o arquivo, escolha as opções desejadas e deixe o vrHouse cuidar do resto."
            ),
            justify=tk.LEFT,
            wraplength=600,
        )
        header.grid(row=0, column=0, columnspan=3, sticky="w", **padding)

        ttk.Label(self, text="Arquivo da planta 3D").grid(row=1, column=0, sticky="w", **padding)
        self.source_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.source_var, width=60).grid(row=1, column=1, sticky="ew", **padding)
        ttk.Button(self, text="Procurar", command=self._browse_source).grid(row=1, column=2, sticky="ew", **padding)

        ttk.Label(self, text="Pasta de saída").grid(row=2, column=0, sticky="w", **padding)
        self.output_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.output_var, width=60).grid(row=2, column=1, sticky="ew", **padding)
        ttk.Button(self, text="Selecionar", command=self._browse_output).grid(row=2, column=2, sticky="ew", **padding)

        ttk.Label(self, text="Nome do projeto").grid(row=3, column=0, sticky="w", **padding)
        self.project_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.project_var, width=40).grid(row=3, column=1, sticky="w", **padding)

        self.physics_var = tk.BooleanVar(value=True)
        self.ai_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Aplicar física realista", variable=self.physics_var).grid(
            row=4, column=0, columnspan=2, sticky="w", **padding
        )
        ttk.Checkbutton(self, text="Melhorar materiais com IA", variable=self.ai_var).grid(
            row=5, column=0, columnspan=2, sticky="w", **padding
        )

        ttk.Label(self, text="Chave de criptografia (opcional)").grid(row=6, column=0, sticky="w", **padding)
        self.key_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.key_var, width=60).grid(row=6, column=1, sticky="ew", **padding)
        ttk.Button(self, text="Gerar chave", command=self._generate_key).grid(row=6, column=2, sticky="ew", **padding)

        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate", maximum=100)
        self.progress.grid(row=7, column=0, columnspan=3, sticky="ew", padx=12, pady=(12, 0))

        self.progress_label = ttk.Label(self, text="Aguardando início da conversão")
        self.progress_label.grid(row=8, column=0, columnspan=3, sticky="w", padx=12, pady=(4, 12))

        action_frame = ttk.Frame(self)
        action_frame.grid(row=9, column=0, columnspan=3, sticky="ew", padx=12, pady=(8, 12))
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)

        self.convert_button = ttk.Button(action_frame, text="Iniciar conversão", command=self._start_conversion)
        self.convert_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.preview_button = ttk.Button(action_frame, text="Visualizar preview", state=tk.DISABLED, command=self._preview)
        self.preview_button.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        self.columnconfigure(1, weight=1)

    def _browse_source(self) -> None:
        suffixes = [f"*{s}" for s in iter_supported_suffixes()]
        path = filedialog.askopenfilename(
            title="Selecione o arquivo 3D",
            filetypes=[("Formatos suportados", " ".join(suffixes))],
        )
        if path:
            self.source_var.set(path)
            suggested_name = Path(path).stem
            if not self.project_var.get():
                self.project_var.set(suggested_name)

    def _browse_output(self) -> None:
        path = filedialog.askdirectory(title="Selecione a pasta de saída")
        if path:
            self.output_var.set(path)

    def _generate_key(self) -> None:
        self.key_var.set(Fernet.generate_key().decode("utf-8"))

    def _start_conversion(self) -> None:
        if self._worker and self._worker.is_alive():
            messagebox.showinfo("Conversão em andamento", "Aguarde a finalização antes de iniciar outra conversão.")
            return

        try:
            specification = self._build_specification()
        except ValueError as exc:
            messagebox.showerror("Dados inválidos", str(exc))
            return

        output_dir = Path(self.output_var.get()).expanduser()

        self.progress_label.config(text="Preparando conversão")
        self.progress.config(value=0)
        self._queue = queue.Queue()
        self._last_result = None
        self.preview_button.config(state=tk.DISABLED)

        def worker() -> None:
            try:
                result = run_conversion(
                    specification,
                    output_dir,
                    progress_callback=lambda progress, message: self._queue.put((progress, message)),
                )
                self._queue.put((1.0, json.dumps({"status": "done", "result": result}, default=str)))
            except Exception as exc:
                self._queue.put((-1.0, str(exc)))

        import threading
        self._worker = threading.Thread(target=worker, daemon=True)
        self._worker.start()
        self._set_controls_enabled(False)

    def _build_specification(self) -> SceneSpecification:
        source = Path(self.source_var.get()).expanduser()
        if not source.exists():
            raise ValueError("Selecione um arquivo 3D válido.")

        project = self.project_var.get().strip()
        if not project:
            raise ValueError("Informe um nome para o projeto.")

        output_dir_value = self.output_var.get().strip()
        if not output_dir_value:
            raise ValueError("Selecione uma pasta de saída.")

        encryption_key = self.key_var.get().strip() or None
        if encryption_key is not None:
            try:
                Fernet(encryption_key.encode("utf-8"))
            except Exception as exc:
                raise ValueError(f"Chave de criptografia inválida: {exc}") from exc

        return SceneSpecification(
            project_name=project,
            source_file=source,
            enable_physics=self.physics_var.get(),
            enable_ai_realism=self.ai_var.get(),
            output_encryption_key=encryption_key,
        )

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        for child in self.winfo_children():
            self._set_state_recursively(child, state)
        self.convert_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)
        if not enabled:
            self.preview_button.configure(state=tk.DISABLED)
        elif self._last_result:
            self.preview_button.configure(state=tk.NORMAL)

    def _set_state_recursively(self, widget: tk.Widget, state: str) -> None:
        if isinstance(widget, (ttk.Entry, ttk.Checkbutton, ttk.Button, ttk.Combobox)):
            widget.configure(state=state)
        if isinstance(widget, (ttk.Frame,)):
            for child in widget.winfo_children():
                self._set_state_recursively(child, state)

    def _poll_updates(self) -> None:
        try:
            while True:
                progress, message = self._queue.get_nowait()
                if progress < 0:
                    self._handle_error(message)
                elif progress >= 1:
                    self._handle_completion(message)
                else:
                    self.progress.config(value=progress * 100)
                    self.progress_label.config(text=message)
        except queue.Empty:
            pass
        finally:
            self.after(200, self._poll_updates)

    def _handle_error(self, message: str) -> None:
        self._set_controls_enabled(True)
        self.progress.config(value=0)
        self.progress_label.config(text="Ocorreu um erro na conversão")
        messagebox.showerror("Falha na conversão", message)
        self._worker = None

    def _handle_completion(self, message: str) -> None:
        self._set_controls_enabled(True)
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            payload = {"status": "done", "result": {}}
        self._last_result = payload.get("result")
        self.progress.config(value=100)
        self.progress_label.config(text="Conversão concluída com sucesso")
        self._worker = None
        if self._last_result:
            self.preview_button.configure(state=tk.NORMAL)
            info = self._last_result
            package = info.get("package_path")
            key = info.get("encryption_key")
            messagebox.showinfo(
                "Conversão finalizada",
                (
                    "Pacote criado em:\n{package}\n\n"
                    "Chave de criptografia:\n{key}\n\n"
                    "Guarde a chave com segurança para abrir o conteúdo nos aplicativos oficiais."
                ).format(package=package, key=key),
            )

    def _preview(self) -> None:
        if not self._last_result:
            messagebox.showinfo("Sem preview", "Realize uma conversão antes de visualizar o preview.")
            return

        package_path = Path(str(self._last_result.get("package_path")))
        key = str(self._last_result.get("encryption_key"))

        try:
            decrypted = self._decrypt_package(package_path, key)
        except (InvalidToken, FileNotFoundError) as exc:
            messagebox.showerror("Preview indisponível", f"Não foi possível abrir o pacote protegido: {exc}")
            return

        preview_window = tk.Toplevel(self)
        preview_window.title("Preview do Projeto")
        preview_window.geometry("480x320")
        text = tk.Text(preview_window, wrap=tk.WORD)
        text.insert(tk.END, json.dumps(decrypted, indent=2, ensure_ascii=False))
        text.configure(state=tk.DISABLED)
        text.pack(expand=True, fill=tk.BOTH)

    def _decrypt_package(self, package_path: Path, key: str) -> dict[str, object]:
        fernet = Fernet(key.encode("utf-8"))
        payload = fernet.decrypt(package_path.read_bytes())
        return json.loads(payload)


def launch() -> None:
    app = VRHouseApp()
    app.mainloop()


__all__ = ["launch", "VRHouseApp"]


if __name__ == "__main__":
    launch()
