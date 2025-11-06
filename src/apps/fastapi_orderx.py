from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Dict
import shutil
from src.agents.inventory_check_agent import inventory_check_agent
from src.agents.order_intake_agent import order_intake_agent
import traceback, json, os

app = FastAPI()

@app.post("/query/image")
async def ask_agent_from_image(
    image: UploadFile = File(...),
    question: str = Form(...)
):
    try:
        # Save image locally
        temp_path = Path("/tmp") / image.filename
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)


        # Build the prompt
        input_prompt = f"{str(temp_path)}   \n{question}"
        response = order_intake_agent(input_prompt)
        #response = await agent_image2text.run_async(input_prompt, max_steps=5)
        print(response)

    
        return JSONResponse(content={"final_answer": response})

    except Exception as e:
        # Print the full stack trace to stdout/logs
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )


@app.get("/inventory/check")
async def check_inventory(input_prompt: str):
    try:
        response = inventory_check_agent(input_prompt)
        print(response)

        return JSONResponse(content={"final_answer": response})
    except Exception as e:
        # Print the full stack trace to stdout/logs
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": traceback.format_exc()
            }
        )
