import json
import textwrap
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk


# =========================================================
# CONFIGURAÇÃO
# =========================================================

FRAME_PATH = "./templates/creatures/Danian Template.png"
BASE_IMAGE_PATH = "./Aszil.jpeg"
OUTPUT_PATH = "./resultado_final.png"
CALIBRATION_PATH = "./calibracao.json"

BASE_POSITION = (21, 51)
BASE_SIZE = (457, 383)
CANVAS_SIZE = (500, 700)
CANVAS_COLOR = (255, 255, 255, 255)

TEXT_ITEMS = [
    {
        "id": "titulo",
        "content": "Aszil",
        "position": (275, 34),
        "box_width": 380,
        "box_height": 36,
        "align": "center",
        "anchor": "center",
        "font_path": "arial.ttf",
        "font_size": 20,
        "color": (255, 255, 255, 255),
        "line_spacing": 8,
        "debug_box_outline": "#00FF00",
        "debug_box_width": 2,
        "debug_box_dash": (6, 3),
        "show_debug_box": True,
    },
    {
        "id": "courage value",
        "content": "999",
        "position": (68, 470),
        "box_width": 40,
        "box_height": 18,
        "align": "center",
        "anchor": "se",
        "font_path": "arial.ttf",
        "font_size": 14,
        "color": (0, 0, 0, 0),
        "line_spacing": 8,
        "debug_box_outline": "#00FF00",
        "debug_box_width": 2,
        "debug_box_dash": (6, 3),
        "show_debug_box": True,
    },
    {
        "id": "power value",
        "content": "999",
        "position": (68, 518),
        "box_width": 40,
        "box_height": 18,
        "align": "center",
        "anchor": "se",
        "font_path": "arial.ttf",
        "font_size": 14,
        "color": (0, 0, 0, 0),
        "line_spacing": 8,
        "debug_box_outline": "#00FF00",
        "debug_box_width": 2,
        "debug_box_dash": (6, 3),
        "show_debug_box": True,
    },
    {
        "id": "wisdom value",
        "content": "999",
        "position": (68, 566),
        "box_width": 40,
        "box_height": 18,
        "align": "center",
        "anchor": "se",
        "font_path": "arial.ttf",
        "font_size": 14,
        "color": (0, 0, 0, 0),
        "line_spacing": 8,
        "debug_box_outline": "#00FF00",
        "debug_box_width": 2,
        "debug_box_dash": (6, 3),
        "show_debug_box": True,
    },
    {
        "id": "speed value",
        "content": "999",
        "position": (68, 614),
        "box_width": 40,
        "box_height": 18,
        "align": "center",
        "anchor": "se",
        "font_path": "arial.ttf",
        "font_size": 14,
        "color": (0, 0, 0, 0),
        "line_spacing": 8,
        "debug_box_outline": "#00FF00",
        "debug_box_width": 2,
        "debug_box_dash": (6, 3),
        "show_debug_box": True,
    }
]


# =========================================================
# LÓGICA DE TEXTO
# =========================================================

PILLOW_ANCHOR_MAP = {
    "nw": "la",
    "n": "ma",
    "ne": "ra",
    "w": "lm",
    "center": "mm",
    "e": "rm",
    "sw": "ld",
    "s": "md",
    "se": "rd",
}

TK_ANCHOR_MAP = {
    "nw": "nw",
    "n": "n",
    "ne": "ne",
    "w": "w",
    "center": "center",
    "e": "e",
    "sw": "sw",
    "s": "s",
    "se": "se",
}


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



def get_font_candidates(font_path: str):
    candidates = []
    if font_path:
        candidates.append(font_path)
        fp = Path(font_path)
        if not fp.is_absolute():
            candidates.extend([
                str(Path.cwd() / font_path),
                str(Path.cwd() / "fonts" / font_path),
            ])
    candidates.extend([
        "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/Library/Fonts/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ])
    seen = []
    for item in candidates:
        if item and item not in seen:
            seen.append(item)
    return seen



def load_font(font_path: str, font_size: int):
    for candidate in get_font_candidates(font_path):
        try:
            return ImageFont.truetype(candidate, font_size)
        except Exception:
            continue
    return ImageFont.load_default()



def measure_text(draw, text, font, spacing):
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="left")
    return bbox[2] - bbox[0], bbox[3] - bbox[1]



def wrap_text_to_width(draw, content, font, max_width, spacing):
    if not content:
        return ""
    paragraphs = content.splitlines() or [content]
    wrapped_paragraphs = []

    for paragraph in paragraphs:
        words = paragraph.split()
        if not words:
            wrapped_paragraphs.append("")
            continue

        lines = []
        current = words[0]
        for word in words[1:]:
            test = f"{current} {word}"
            width, _ = measure_text(draw, test, font, spacing)
            if width <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)

        adjusted = []
        for line in lines:
            width, _ = measure_text(draw, line, font, spacing)
            if width <= max_width:
                adjusted.append(line)
                continue
            broken = textwrap.wrap(line, width=max(1, int(len(line) * max_width / max(width, 1)))) or [line]
            for part in broken:
                adjusted.append(part)
        wrapped_paragraphs.append("\n".join(adjusted))

    return "\n".join(wrapped_paragraphs)



def get_box_rectangle(x, y, box_width, box_height, anchor="nw"):
    if anchor == "nw":
        left, top = x, y
    elif anchor == "n":
        left, top = x - box_width // 2, y
    elif anchor == "ne":
        left, top = x - box_width, y
    elif anchor == "w":
        left, top = x, y - box_height // 2
    elif anchor == "center":
        left, top = x - box_width // 2, y - box_height // 2
    elif anchor == "e":
        left, top = x - box_width, y - box_height // 2
    elif anchor == "sw":
        left, top = x, y - box_height
    elif anchor == "s":
        left, top = x - box_width // 2, y - box_height
    elif anchor == "se":
        left, top = x - box_width, y - box_height
    else:
        left, top = x, y
    right = left + box_width
    bottom = top + box_height
    return left, top, right, bottom



def get_textbox_layout(draw, text_item, font):
    x, y = text_item["position"]
    box_width = text_item.get("box_width", 300)
    box_height = text_item.get("box_height", 120)
    anchor = text_item.get("anchor", "nw")
    spacing = text_item.get("line_spacing", 4)
    align = text_item.get("align", "left")
    x1, y1, x2, y2 = get_box_rectangle(x, y, box_width, box_height, anchor)
    wrapped_text = wrap_text_to_width(draw, text_item.get("content", ""), font, box_width, spacing)
    text_w, text_h = measure_text(draw, wrapped_text or " ", font, spacing)

    if align == "center":
        text_x = x1 + box_width / 2
    elif align == "right":
        text_x = x2
    else:
        text_x = x1

    text_y = y1 + box_height / 2
    pillow_anchor = {
        "left": "lm",
        "center": "mm",
        "right": "rm",
    }.get(align, "lm")

    return {
        "box": (x1, y1, x2, y2),
        "wrapped_text": wrapped_text,
        "text_size": (text_w, text_h),
        "draw_xy": (text_x, text_y),
        "pillow_anchor": pillow_anchor,
    }



def add_textboxes(image: Image.Image, text_items: list[dict], draw_debug=False) -> Image.Image:
    result = image.copy()
    draw = ImageDraw.Draw(result)

    for item in text_items:
        font = load_font(item.get("font_path", ""), item.get("font_size", 24))
        layout = get_textbox_layout(draw, item, font)
        draw.multiline_text(
            layout["draw_xy"],
            layout["wrapped_text"],
            font=font,
            fill=item.get("color", (0, 0, 0, 255)),
            spacing=item.get("line_spacing", 4),
            align=item.get("align", "left"),
            anchor=layout["pillow_anchor"],
        )

        if draw_debug and item.get("show_debug_box", True):
            draw.rectangle(
                layout["box"],
                outline=item.get("debug_box_outline", "#00FF00"),
                width=item.get("debug_box_width", 1),
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
    text_items=None,
    draw_debug=False,
):
    text_items = text_items or []
    frame = load_image(frame_path)
    base = load_image(base_image_path)
    base = resize_image(base, base_size)

    final_canvas_size = canvas_size or frame.size
    canvas = create_canvas(final_canvas_size, canvas_color)

    composed = paste_base_image(canvas, base, base_position)
    composed = overlay_frame(composed, frame)
    composed = add_textboxes(composed, text_items, draw_debug=draw_debug)

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

        self._build_ui()
        self._build_canvas_scene()
        self._refresh_preview()
        self._update_info_panel()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)

        left = ttk.Frame(container)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(container, width=340)
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

        ttk.Button(right, text="Alternar debug da caixa", command=self.toggle_selected_debug_box).pack(fill="x", pady=4)

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
        self.canvas_items["frame"] = self.canvas.create_image(0, 0, image=self.tk_cache["frame"], anchor="nw")

        for text_item in self.text_items:
            rect_id = self.canvas.create_rectangle(0, 0, 1, 1, dash=text_item.get("debug_box_dash", (6, 3)), outline=text_item.get("debug_box_outline", "#00FF00"), width=text_item.get("debug_box_width", 1), state="normal")
            self.canvas_items[f"text_rect::{text_item['id']}"] = rect_id

            item_id = self.canvas.create_text(
                text_item["position"][0],
                text_item["position"][1],
                text=text_item["content"],
                fill=self._rgba_to_hex(text_item.get("color", (255, 255, 255, 255))),
                font=("Arial", text_item.get("font_size", 24), "bold"),
                anchor=TK_ANCHOR_MAP.get(text_item.get("anchor", "nw"), "nw"),
                width=text_item.get("box_width", 300),
                justify=text_item.get("align", "left"),
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
        self._update_debug_rectangles()
        self._update_info_panel()

    def stop_drag(self, event):
        self._sync_positions_from_canvas()
        self._update_debug_rectangles()
        self._update_info_panel()
        self.selected_item = None

    def _sync_positions_from_canvas(self):
        base_coords = self.canvas.coords(self.canvas_items["base"])
        self.base_position = [int(base_coords[0]), int(base_coords[1])]
        for item in self.text_items:
            canvas_id = self.canvas_items[f"text::{item['id']}"]
            coords = self.canvas.coords(canvas_id)
            item["position"] = (int(coords[0]), int(coords[1]))

    def _update_debug_rectangles(self):
        for item in self.text_items:
            self.update_text_box_rectangle(item)

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
        self._update_debug_rectangles()
        self._update_info_panel()

    def toggle_selected_debug_box(self):
        text_id = self.get_selected_text_id()
        if not text_id:
            messagebox.showinfo("Seleção", "Selecione um texto na lista.")
            return
        item = next(x for x in self.text_items if x["id"] == text_id)
        item["show_debug_box"] = not item.get("show_debug_box", True)
        self.update_text_box_rectangle(item)

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
            "Imagem base:",
            f"  x={self.base_position[0]}, y={self.base_position[1]}",
            f"  largura={self.base_image.size[0]}, altura={self.base_image.size[1]}",
            "",
            "Textos:",
        ]
        for item in self.text_items:
            x, y = item["position"]
            lines.append(
                f"  {item['id']}: x={x}, y={y}, size={item.get('font_size', 24)}, width={item.get('box_width', 0)}, anchor={item.get('anchor', 'nw')}, align={item.get('align', 'left')}"
            )
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
                    "box_width": item.get("box_width", 300),
                    "box_height": item.get("box_height", 120),
                    "align": item.get("align", "left"),
                    "anchor": item.get("anchor", "nw"),
                    "font_path": item.get("font_path", ""),
                    "font_size": item.get("font_size", 24),
                    "color": list(item.get("color", (0, 0, 0, 255))),
                    "line_spacing": item.get("line_spacing", 4),
                    "debug_box_outline": item.get("debug_box_outline", "#00FF00"),
                    "debug_box_width": item.get("debug_box_width", 1),
                    "debug_box_dash": list(item.get("debug_box_dash", (6, 3))),
                    "show_debug_box": item.get("show_debug_box", True),
                }
                for item in self.text_items
            ]
        }

    def save_calibration(self):
        data = self.build_calibration_dict()
        Path(CALIBRATION_PATH).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
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
            text_items=self.text_items,
            draw_debug=False,
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
                font=("Arial", item.get("font_size", 24), "bold"),
                width=item.get("box_width", 300),
                justify=item.get("align", "left"),
                anchor=TK_ANCHOR_MAP.get(item.get("anchor", "nw"), "nw"),
            )
            self.update_text_box_rectangle(item)

        self.canvas.lift(self.canvas_items["frame"])
        for item in self.text_items:
            self.canvas.lift(self.canvas_items[f"text_rect::{item['id']}"])
            self.canvas.lift(self.canvas_items[f"text::{item['id']}"])
        self._update_info_panel()

    def update_text_box_rectangle(self, text_item):
        rect_id = self.canvas_items[f"text_rect::{text_item['id']}"]
        x, y = text_item["position"]
        box_width = text_item.get("box_width", 300)
        box_height = text_item.get("box_height", 120)
        anchor = text_item.get("anchor", "nw")
        x1, y1, x2, y2 = get_box_rectangle(x, y, box_width, box_height, anchor)
        self.canvas.coords(rect_id, x1, y1, x2, y2)
        self.canvas.itemconfigure(
            rect_id,
            outline=text_item.get("debug_box_outline", "#00FF00"),
            width=text_item.get("debug_box_width", 1),
            dash=text_item.get("debug_box_dash", (6, 3)),
            state="normal" if text_item.get("show_debug_box", True) else "hidden",
        )
        self.canvas.tag_raise(rect_id)


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CalibrationEditor(root)
    root.mainloop()
