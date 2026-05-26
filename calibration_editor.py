import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk

# =========================================================
# CONFIGURAÇÃO
# =========================================================

FRAME_PATH = "./templates/creatures/Danian_Template.png"
BASE_IMAGE_PATH = "./Aszil.jpeg"
OUTPUT_PATH = "./resultado_final.png"
CALIBRATION_PATH = "./calibracao.json"

BASE_POSITION = (21, 51)
BASE_SIZE = (457, 383)   # None para manter original
CANVAS_SIZE = (500, 700)
CANVAS_COLOR = (255, 255, 255, 255)

TEXT_ITEMS = [
    {
        "id": "titulo",
        "content": "Aszil",
        "position": (240, 14),
        "font_path": "arial.ttf",
        "font_size": 16,
        "color": (255, 255, 255, 255)
    },
    {
        "id": "subtitulo",
        "content": "the Young Queen",
        "position": (190, 35),
        "font_path": "arial.ttf",
        "font_size": 12,
        "color": (255, 215, 0, 255)
    }
]

# =========================================================
# LÓGICA DE COMPOSIÇÃO
# =========================================================

def load_image(image_path: str) -> Image.Image:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
    return Image.open(path).convert("RGBA")


def resize_image(image: Image.Image, size=None) -> Image.Image:
    if size is None:
        return image
    return image.resize(size, Image.Resampling.LANCZOS)


def create_canvas(size, color=(255, 255, 255, 255)) -> Image.Image:
    return Image.new("RGBA", size, color)


def paste_base_image(canvas: Image.Image, base_image: Image.Image, position):
    result = canvas.copy()
    result.paste(base_image, position, base_image)
    return result


def overlay_frame(composed_image: Image.Image, frame_image: Image.Image) -> Image.Image:
    if frame_image.size != composed_image.size:
        frame_image = frame_image.resize(composed_image.size, Image.Resampling.LANCZOS)

    result = composed_image.copy()
    result.paste(frame_image, (0, 0), frame_image)
    return result


def load_font(font_path: str, font_size: int):
    try:
        if font_path and Path(font_path).exists():
            return ImageFont.truetype(font_path, font_size)
        return ImageFont.truetype(font_path, font_size)
    except Exception:
        return ImageFont.load_default()


def add_texts(image: Image.Image, text_items: list[dict]) -> Image.Image:
    result = image.copy()
    draw = ImageDraw.Draw(result)

    for item in text_items:
        font = load_font(item.get("font_path", ""), item.get("font_size", 24))
        draw.text(
            item["position"],
            item["content"],
            font=font,
            fill=item.get("color", (0, 0, 0, 255))
        )

    return result


def save_image(image: Image.Image, output_path: str) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def compose_image(
    frame_path,
    base_image_path,
    output_path,
    base_position,
    base_size=None,
    canvas_size=None,
    canvas_color=(255, 255, 255, 255),
    text_items=None
):
    text_items = text_items or []

    frame = load_image(frame_path)
    base = load_image(base_image_path)
    base = resize_image(base, base_size)

    final_canvas_size = canvas_size or frame.size
    canvas = create_canvas(final_canvas_size, canvas_color)

    composed = paste_base_image(canvas, base, base_position)
    composed = overlay_frame(composed, frame)
    composed = add_texts(composed, text_items)

    save_image(composed, output_path)
    return composed


# =========================================================
# EDITOR DE CALIBRAÇÃO
# =========================================================

class CalibrationEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Calibração de composição")
        self.root.geometry("1600x950")

        self.base_position = list(BASE_POSITION)
        self.base_size = BASE_SIZE
        self.text_items = [dict(item) for item in TEXT_ITEMS]

        self.selected_item = None
        self.drag_data = {"x": 0, "y": 0}

        self.original_frame = load_image(FRAME_PATH)
        self.original_base = load_image(BASE_IMAGE_PATH)
        self.base_image = resize_image(self.original_base, self.base_size)

        self.canvas_width, self.canvas_height = CANVAS_SIZE

        self.tk_cache = {}
        self.canvas_items = {}
        self.text_labels = {}

        self._build_ui()
        self._build_canvas_scene()
        self._refresh_preview()
        self._update_info_panel()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)

        left = ttk.Frame(container)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(container, width=320)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        self.canvas = tk.Canvas(
            left,
            width=min(self.canvas_width, 1200),
            height=min(self.canvas_height, 850),
            bg="#2b2b2b",
            highlightthickness=1,
            highlightbackground="#666"
        )
        self.canvas.pack(fill="both", expand=True)

        ttk.Label(right, text="Controles", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

        self.info_var = tk.StringVar()
        ttk.Label(right, textvariable=self.info_var, justify="left").pack(anchor="w", fill="x", pady=(0, 10))

        ttk.Label(right, text="Mover imagem base").pack(anchor="w")
        move_frame = ttk.Frame(right)
        move_frame.pack(anchor="w", pady=(4, 12))

        ttk.Button(move_frame, text="←", width=4, command=lambda: self.nudge_item("base", -1, 0)).grid(row=0, column=0)
        ttk.Button(move_frame, text="→", width=4, command=lambda: self.nudge_item("base", 1, 0)).grid(row=0, column=1)
        ttk.Button(move_frame, text="↑", width=4, command=lambda: self.nudge_item("base", 0, -1)).grid(row=0, column=2)
        ttk.Button(move_frame, text="↓", width=4, command=lambda: self.nudge_item("base", 0, 1)).grid(row=0, column=3)

        ttk.Label(right, text="Redimensionar imagem base").pack(anchor="w")
        resize_frame = ttk.Frame(right)
        resize_frame.pack(anchor="w", pady=(4, 12))

        ttk.Button(resize_frame, text="- largura", command=lambda: self.resize_base(-10, 0)).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(resize_frame, text="+ largura", command=lambda: self.resize_base(10, 0)).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(resize_frame, text="- altura", command=lambda: self.resize_base(0, -10)).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(resize_frame, text="+ altura", command=lambda: self.resize_base(0, 10)).grid(row=1, column=1, padx=2, pady=2)

        ttk.Separator(right).pack(fill="x", pady=10)

        ttk.Label(right, text="Textos").pack(anchor="w")
        self.text_list = tk.Listbox(right, height=6)
        self.text_list.pack(fill="x", pady=(4, 8))
        for item in self.text_items:
            self.text_list.insert("end", item["id"])
        self.text_list.bind("<<ListboxSelect>>", self._on_text_select)

        text_move = ttk.Frame(right)
        text_move.pack(anchor="w", pady=(0, 12))
        ttk.Button(text_move, text="← texto", command=lambda: self.nudge_selected_text(-1, 0)).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(text_move, text="→ texto", command=lambda: self.nudge_selected_text(1, 0)).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(text_move, text="↑ texto", command=lambda: self.nudge_selected_text(0, -1)).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(text_move, text="↓ texto", command=lambda: self.nudge_selected_text(0, 1)).grid(row=1, column=1, padx=2, pady=2)

        ttk.Separator(right).pack(fill="x", pady=10)

        ttk.Button(right, text="Exportar imagem final", command=self.export_final).pack(fill="x", pady=4)
        ttk.Button(right, text="Salvar calibração (JSON)", command=self.save_calibration).pack(fill="x", pady=4)
        ttk.Button(right, text="Recarregar preview", command=self._refresh_preview).pack(fill="x", pady=4)

        ttk.Label(
            right,
            text="Dica: arraste com o mouse a imagem base ou os textos diretamente no preview.",
            wraplength=280,
            justify="left"
        ).pack(anchor="w", pady=(12, 0))

    def _build_canvas_scene(self):
        bg = Image.new("RGBA", CANVAS_SIZE, CANVAS_COLOR)
        self.tk_cache["bg"] = ImageTk.PhotoImage(bg)
        self.canvas_items["bg"] = self.canvas.create_image(0, 0, image=self.tk_cache["bg"], anchor="nw")

        self.tk_cache["base"] = ImageTk.PhotoImage(self.base_image)
        self.canvas_items["base"] = self.canvas.create_image(
            self.base_position[0],
            self.base_position[1],
            image=self.tk_cache["base"],
            anchor="nw",
            tags=("draggable", "base")
        )

        frame = self.original_frame
        if frame.size != CANVAS_SIZE:
            frame = frame.resize(CANVAS_SIZE, Image.Resampling.LANCZOS)
        self.tk_cache["frame"] = ImageTk.PhotoImage(frame)
        self.canvas_items["frame"] = self.canvas.create_image(
            0, 0,
            image=self.tk_cache["frame"],
            anchor="nw"
        )

        for text_item in self.text_items:
            item_id = self.canvas.create_text(
                text_item["position"][0],
                text_item["position"][1],
                text=text_item["content"],
                fill=self._rgba_to_hex(text_item.get("color", (255, 255, 255, 255))),
                font=("Arial", text_item.get("font_size", 24), "bold"),
                anchor="nw",
                tags=("draggable", f"text::{text_item['id']}")
            )
            self.canvas_items[f"text::{text_item['id']}"] = item_id

        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.start_drag)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.do_drag)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.stop_drag)

    def _rgba_to_hex(self, rgba):
        r, g, b = rgba[:3]
        return f"#{r:02x}{g:02x}{b:02x}"

    def start_drag(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return
        self.selected_item = item[0]
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def do_drag(self, event):
        if not self.selected_item:
            return

        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]

        self.canvas.move(self.selected_item, dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

        self._sync_positions_from_canvas()
        self._update_info_panel()

    def stop_drag(self, event):
        self._sync_positions_from_canvas()
        self._update_info_panel()
        self.selected_item = None

    def _sync_positions_from_canvas(self):
        base_coords = self.canvas.coords(self.canvas_items["base"])
        self.base_position = [int(base_coords[0]), int(base_coords[1])]

        for item in self.text_items:
            canvas_id = self.canvas_items[f"text::{item['id']}"]
            coords = self.canvas.coords(canvas_id)
            item["position"] = (int(coords[0]), int(coords[1]))

    def nudge_item(self, item_name, dx, dy):
        canvas_id = self.canvas_items.get(item_name)
        if not canvas_id:
            return
        self.canvas.move(canvas_id, dx, dy)
        self._sync_positions_from_canvas()
        self._update_info_panel()

    def _on_text_select(self, event=None):
        self._update_info_panel()

    def get_selected_text_id(self):
        selection = self.text_list.curselection()
        if not selection:
            return None
        index = selection[0]
        return self.text_items[index]["id"]

    def nudge_selected_text(self, dx, dy):
        text_id = self.get_selected_text_id()
        if not text_id:
            messagebox.showinfo("Seleção", "Selecione um texto na lista.")
            return

        canvas_id = self.canvas_items[f"text::{text_id}"]
        self.canvas.move(canvas_id, dx, dy)
        self._sync_positions_from_canvas()
        self._update_info_panel()

    def resize_base(self, dw, dh):
        current_w, current_h = self.base_image.size
        new_w = max(20, current_w + dw)
        new_h = max(20, current_h + dh)

        self.base_size = (new_w, new_h)
        self.base_image = resize_image(self.original_base, self.base_size)

        self.tk_cache["base"] = ImageTk.PhotoImage(self.base_image)
        self.canvas.itemconfigure(self.canvas_items["base"], image=self.tk_cache["base"])

        self._update_info_panel()

    def _update_info_panel(self):
        lines = [
            f"Imagem base:",
            f"  x={self.base_position[0]}, y={self.base_position[1]}",
            f"  largura={self.base_image.size[0]}, altura={self.base_image.size[1]}",
            ""
        ]

        lines.append("Textos:")
        for item in self.text_items:
            x, y = item["position"]
            lines.append(f"  {item['id']}: x={x}, y={y}, size={item.get('font_size', 24)}")

        self.info_var.set("\n".join(lines))

    def build_calibration_dict(self):
        return {
            "frame_path": FRAME_PATH,
            "base_image_path": BASE_IMAGE_PATH,
            "output_path": OUTPUT_PATH,
            "canvas_size": list(CANVAS_SIZE),
            "canvas_color": list(CANVAS_COLOR),
            "base_position": list(self.base_position),
            "base_size": list(self.base_size) if self.base_size else None,
            "texts": [
                {
                    "id": item["id"],
                    "content": item["content"],
                    "position": list(item["position"]),
                    "font_path": item.get("font_path", ""),
                    "font_size": item.get("font_size", 24),
                    "color": list(item.get("color", (0, 0, 0, 255)))
                }
                for item in self.text_items
            ]
        }

    def save_calibration(self):
        data = self.build_calibration_dict()
        Path(CALIBRATION_PATH).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        messagebox.showinfo("Sucesso", f"Calibração salva em:\n{CALIBRATION_PATH}")

    def export_final(self):
        compose_image(
            frame_path=FRAME_PATH,
            base_image_path=BASE_IMAGE_PATH,
            output_path=OUTPUT_PATH,
            base_position=tuple(self.base_position),
            base_size=self.base_size,
            canvas_size=CANVAS_SIZE,
            canvas_color=CANVAS_COLOR,
            text_items=self.text_items
        )
        messagebox.showinfo("Sucesso", f"Imagem exportada para:\n{OUTPUT_PATH}")

    def _refresh_preview(self):
        composed_preview = create_canvas(CANVAS_SIZE, CANVAS_COLOR)
        composed_preview = paste_base_image(composed_preview, self.base_image, tuple(self.base_position))

        self.tk_cache["preview_base"] = ImageTk.PhotoImage(composed_preview)
        self.canvas.itemconfigure(self.canvas_items["bg"], image=self.tk_cache["preview_base"])
        self.canvas.coords(self.canvas_items["bg"], 0, 0)

        self.canvas.coords(self.canvas_items["base"], self.base_position[0], self.base_position[1])

        for item in self.text_items:
            canvas_id = self.canvas_items[f"text::{item['id']}"]
            self.canvas.coords(canvas_id, item["position"][0], item["position"][1])
            self.canvas.itemconfigure(
                canvas_id,
                text=item["content"],
                fill=self._rgba_to_hex(item.get("color", (255, 255, 255, 255))),
                font=("Arial", item.get("font_size", 24), "bold")
            )

        self.canvas.lift(self.canvas_items["frame"])
        for item in self.text_items:
            self.canvas.lift(self.canvas_items[f"text::{item['id']}"])

        self._update_info_panel()


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CalibrationEditor(root)
    root.mainloop()