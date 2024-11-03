import pymupdf,os,base64

def convert_pdf_to_image(pdf_file_path):
    doc = pymupdf.open(pdf_file_path)
    fname = os.path.splitext(os.path.basename(pdf_file_path))
    path = os.path.join("img_files",fname[0])
    for page in doc:
        pix = page.get_pixmap()
        pix.save(f"{path}-%i.jpeg" % page.number)
    return "img_files"

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def get_image_prompt(file_path):
    img_prompt = []
    if os.path.isdir(file_path):
        for file in os.listdir(file_path):
            img_prompt.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encode_image(os.path.join(file_path,file))}"
            }})
    else:
        img_prompt = [{
            "type":"image_url",
            "image_url": {
                "url": f"data:image/jpeg,base64,{encode_image(file_path)}"
            }
        }]
    return img_prompt