from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# =========================================================
# CONFIGURAÇÃO
# =========================================================

FRAME_PATH = "template/Danian Template.png"
BASE_IMAGE_PATH = "Aszil.jpeg"
OUTPUT_PATH = "resultado_final.png"

# Posição da imagem base dentro da composição final
BASE_POSITION = (21, 51)  # (x, y)

# Tamanho opcional da imagem base.
# Use None para manter o tamanho original.
BASE_SIZE = (457, 383)  # (largura, altura) ou None

# Cor de fundo do canvas final caso a moldura tenha áreas transparentes
# e a imagem base não ocupe tudo.
CANVAS_SIZE = (500, 700)  # (largura, altura) do canvas final
CANVAS_COLOR = (255, 255, 255, 255)  # branco RGBA

# Lista de textos a serem inseridos
TEXT_ITEMS = [
    {
        "content": "Exemplo de título",
        "position": (140, 60),
        "font_path": "arial.ttf",   # ajuste para uma fonte existente no seu sistema
        "font_size": 48,
        "color": (255, 255, 255, 255)
    },
    {
        "content": "Subtítulo posicionado por coordenadas",
        "position": (140, 120),
        "font_path": "arial.ttf",
        "font_size": 28,
        "color": (255, 215, 0, 255)
    }
]

# =========================================================
# FUNÇÕES
# =========================================================

def load_image(image_path: str) -> Image.Image:
    """
    Carrega uma imagem e converte para RGBA.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
    return Image.open(path).convert("RGBA")


def resize_image(image: Image.Image, size=None) -> Image.Image:
    """
    Redimensiona a imagem se 'size' for informado.
    """
    if size is None:
        return image
    return image.resize(size, Image.Resampling.LANCZOS)


def create_canvas(size, color=(255, 255, 255, 255)) -> Image.Image:
    """
    Cria um canvas RGBA para a composição final.
    """
    return Image.new("RGBA", size, color)


def paste_base_image(canvas: Image.Image, base_image: Image.Image, position: tuple[int, int]) -> Image.Image:
    """
    Cola a imagem base no canvas usando transparência, se houver.
    """
    result = canvas.copy()
    result.paste(base_image, position, base_image)
    return result


def overlay_frame(composed_image: Image.Image, frame_image: Image.Image) -> Image.Image:
    """
    Sobrepõe a moldura por cima da composição.
    A moldura deve ter o mesmo tamanho do canvas final.
    """
    if frame_image.size != composed_image.size:
        raise ValueError(
            f"A moldura precisa ter o mesmo tamanho da composição final. "
            f"Moldura: {frame_image.size}, composição: {composed_image.size}"
        )

    result = composed_image.copy()
    result.paste(frame_image, (0, 0), frame_image)
    return result


def load_font(font_path: str, font_size: int):
    """
    Tenta carregar uma fonte TrueType/OpenType.
    Se falhar, usa a fonte padrão do Pillow.
    """
    try:
        if font_path and Path(font_path).exists():
            return ImageFont.truetype(font_path, font_size)
        return ImageFont.truetype(font_path, font_size)
    except Exception:
        return ImageFont.load_default()


def add_texts(image: Image.Image, text_items: list[dict]) -> Image.Image:
    """
    Adiciona múltiplos textos à imagem.
    """
    result = image.copy()
    draw = ImageDraw.Draw(result)

    for item in text_items:
        content = item["content"]
        position = item["position"]
        font_path = item.get("font_path", "")
        font_size = item.get("font_size", 24)
        color = item.get("color", (0, 0, 0, 255))

        font = load_font(font_path, font_size)
        draw.text(position, content, font=font, fill=color)

    return result


def save_image(image: Image.Image, output_path: str) -> None:
    """
    Salva a imagem final.
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def compose_image(
    frame_path: str,
    base_image_path: str,
    output_path: str,
    base_position: tuple[int, int],
    base_size=None,
    canvas_size=None,
    canvas_color=(255, 255, 255, 255),
    text_items=None
) -> None:
    """
    Fluxo principal de composição:
    1. carrega moldura e imagem base
    2. redimensiona a imagem base, se necessário
    3. cria canvas
    4. cola imagem base
    5. aplica moldura
    6. adiciona textos
    7. salva resultado
    """
    text_items = text_items or []

    frame = load_image(frame_path)
    base = load_image(base_image_path)
    base = resize_image(base, base_size)

    final_canvas_size = canvas_size or frame.size
    canvas = create_canvas(final_canvas_size, canvas_color)

    composed = paste_base_image(canvas, base, base_position)

    # Se o canvas foi definido manualmente, a moldura precisa combinar com ele
    # ou então pode ser redimensionada.
    if frame.size != final_canvas_size:
        frame = frame.resize(final_canvas_size, Image.Resampling.LANCZOS)

    composed = overlay_frame(composed, frame)
    composed = add_texts(composed, text_items)

    save_image(composed, output_path)


# =========================================================
# EXEMPLO DE USO
# =========================================================

if __name__ == "__main__":
    try:
        compose_image(
            frame_path=FRAME_PATH,
            base_image_path=BASE_IMAGE_PATH,
            output_path=OUTPUT_PATH,
            base_position=BASE_POSITION,
            base_size=BASE_SIZE,
            canvas_size=CANVAS_SIZE,
            canvas_color=CANVAS_COLOR,
            text_items=TEXT_ITEMS
        )
        print(f"Imagem final salva em: {OUTPUT_PATH}")
    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")