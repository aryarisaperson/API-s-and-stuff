from config import HF_API_KEY
import requests, io, json
from PIL import Image
from colorama import Fore, Style, init
init(autoreset=True)

def getcaption(image):
    url = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    bufferr = io.BytesIO()
    image.save(bufferr, format="JPEG")
    res = requests.post(url, headers=headers, data=bufferr.getvalue())
    return res.json()[0]["generated_text"]



def expand_caption(caption):
    url = "https://api-inference.huggingface.co/models/gpt2"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": f"Expand this caption into 30 words: {caption}", "parameters": {"max_new_tokens": 50}}
    res = requests.post(url, headers=headers, json=payload)
    text = json.loads(res.content)[0]["generated_text"]
    return " ".join(text.split()[:30])

def main():
    path = input("pls enter image path\n- ").strip()
    try:
        image = Image.open(path)
        print(Fore.YELLOW + "captionm generating")
        caption = getcaption(image)
        print(Fore.GREEN + "here is ur caption\n-  " + Style.BRIGHT + caption)
        expan = input("want 2 expand to 30 words?(y/n)\n-  ").strip().lower()
        if expan == "y":
            print(Fore.YELLOW + "expanding.....")
            description = expand_caption(caption)
            print(Fore.GREEN + "success\n- " + Style.BRIGHT + description)
    except Exception as e:
        print(Fore.RED + f"error: {e}")



if __name__ == "__main__":
    main()