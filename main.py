import os
import subprocess
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
import shutil

app = FastAPI()

# Update the directories for Docker
BASE_DIR = "/app/downloads"
MODELS_DIR = "/app/models"
PARSED_DIR = "/app/parsed/magic-pdf"
OUTPUT_DIR = "auto"

# Ensure the parsed directory exists with the correct permissions
os.makedirs(PARSED_DIR, exist_ok=True)
os.chmod(PARSED_DIR, 0o755)


@app.post("/process-pdf/")
async def process_pdf(pdf: UploadFile = File(...)):
    pdf_name = pdf.filename
    pdf_path = os.path.join(BASE_DIR, pdf_name)

    # Save the uploaded PDF
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    # Run the magic-pdf command
    result = subprocess.run(
        ["magic-pdf", "pdf-command", "--pdf", pdf_path, "--inside_model", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # env={
        #     "MODELS_DIR": MODELS_DIR
        # },  # Pass the models directory as an environment variable
    )

    if result.returncode != 0:
        return JSONResponse(status_code=500, content={"error": result.stderr.decode()})

    pdf_base_name = Path(pdf_name).stem
    output_path = os.path.join(PARSED_DIR, pdf_base_name, OUTPUT_DIR)

    return {"message": "PDF processed successfully", "output_path": output_path}


@app.get("/get-json/")
async def get_json(pdf_name: str, json_file: str):
    print(
        f"JSON file path: {PARSED_DIR, pdf_name, OUTPUT_DIR, json_file}"
    )  # Print the json_path
    json_path = os.path.join(PARSED_DIR, pdf_name, OUTPUT_DIR, json_file)

    if not os.path.exists(json_path):
        return JSONResponse(status_code=404, content={"error": "JSON file not found"})

    return FileResponse(json_path, media_type="application/json")


@app.get("/get-images/")
async def get_images(pdf_name: str):
    images_dir = os.path.join(PARSED_DIR, pdf_name, OUTPUT_DIR, "images")

    if not os.path.exists(images_dir):
        return JSONResponse(
            status_code=404, content={"error": "Images directory not found"}
        )

    image_files = [
        f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))
    ]
    image_urls = [
        f"/get-image/?pdf_name={pdf_name}&image_file={img}" for img in image_files
    ]

    return {"images": image_urls}


@app.get("/get-image/")
async def get_image(pdf_name: str, image_file: str):
    image_path = os.path.join(PARSED_DIR, pdf_name, OUTPUT_DIR, "images", image_file)

    if not os.path.exists(image_path):
        return JSONResponse(status_code=404, content={"error": "Image file not found"})

    return FileResponse(image_path, media_type="image/jpeg")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
