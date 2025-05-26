import random, os
from uuid import uuid4

def unique_email():
    return f"{''.join([str(random.randint(0, 9)) for _ in range(6)])}@example.com"

def unique_cpf():
    return ''.join([str(random.randint(0, 9)) for _ in range(11)])

def to_str_lower(value):
    if isinstance(value, str):
        return value.lower()
    elif hasattr(value, "value"):
        return str(value.value).lower()
    return str(value).lower()

def handle_upload_images(product, files, images_dir="static/product_images"):
    os.makedirs(images_dir, exist_ok=True)
    if not product.prod_imgs:
        product.prod_imgs = []
    for file in files:
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid4().hex}{ext}"
        file_path = os.path.join(images_dir, filename)
        with open(file_path, "wb") as image_file:
            image_file.write(file.file.read())
        product.prod_imgs.append(f"/static/product_images/{filename}")

def handle_delete_images(product, images_dir="static/product_images"):
    if product.prod_imgs:
        for img_path in product.prod_imgs:
            filename = os.path.basename(img_path)
            file_path = os.path.join(images_dir, filename)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
        product.prod_imgs = []