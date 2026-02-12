import os, io, json, requests
from PIL import Image
from colorama import init, Fore, Style
from config import HF_API_KEY
init(autoreset=True)

def query_hf_api(api_url, payload=None, files=None, method="post"):
    headers= {"Authorization": f"Bearer {HF_API_KEY}"}
    try:
        if method.lower()=="post":
            response=requests.post(api_url, headers=headers, json=payload, files=files)
        else:
            response=requests.post(api_url, headers=headers, params=payload)
        if response.status_code !=200:
            raise Exception(f"Status {response.status_code}: {response.text}")
        return response.content
    except Exception as e:
        print(f"{Fore.RED} sorry, error while calling api at {e}")
        raise

def get_basic_caption(image, model="nlpconnect/vit-gpt2-image-captioning"):
    print(f"{Fore.YELLOW}generating basic caption usign gpt2...")
    api_url=f"https://api-inference.huggingface.co/models/{model}"
    buffered=io.BytesIO()
    image.save(buffered, format="JPEG")
    buffered.seek(0)
    headers={"Authorization": f"Bearer {HF_API_KEY}"}
    response=requests.post(api_url, headers=headers, data=buffered.read())
    result=response.json()
    if isinstance(result, dict) and "error" in result:
        return f"[Error] {result['error']}"
    caption=result[0].get("generated_text", "No caption generated.")
    return caption

def generate_text(prompt, model="gpt2", max_new_tokens=60):
    print(f"{Fore.CYAN}\n- generating text w prompt \n- ({prompt})")
    api_url= f"https://api-inference.hugginhface.co/models/{model}"
    payload={"inputs": prompt, "parameters": {"max_new_tokens": max_new_tokens}}
    text_bytes=query_hf_api(api_url, payload=payload)

    try:
        result=json.loads(text_bytes.decode("utf-8"))
    except Exception as e:
        raise Exception(f"{Fore.RED}failed to decode text generation response")
    
    if isinstance(result, dict) and "error" in result:
        raise Exception(result["error"])

    generated=result[0].get("generated_text", "")
    return generated

def truncate(text, limit):
    words=text.strip().split()
    return " ".join(words[ :limit])

def menu():
    print(f"{Style.BRIGHT}{Fore.GREEN}\n hi, select output tyep, you can choose from \n\n- caption (5 words)\n\n- description(30 words)\n\n- summary(50 words)\n\n- exit")

def main():
    image_path=input(f"{Fore.BLUE}enter image path\n- {Style.RESET_ALL}")
    if not os.path.exists(image_path):
        print(f"{Fore.RED} we couldnt find the path '{image_path}', either the path is wrong or we're just blind")
        return
    
    try:
        image=Image.open(image)
    except Exception as f:
        print(f"{Fore.RED} sorry, we couldnt open image because, '{f}' , we suck at opening things")
        return
    
    basic=get_basic_caption(image)
    print(f"{Fore.YELLOW}\n- basic caption:\n\n- {Style.BRIGHT}{basic}\n")

    while True:
        menu()
        choice=input(f"{Fore.CYAN}enter your choice (1-4)\n -{Style.RESET_ALL}")
        if choice=="1":
            caption=truncate(basic, 5)
            print(f"{Fore.GREEN} here you go:\n\n- {Style.BRIGHT}{caption}\n-")
        elif choice=="2":
            prompt_text=f"do you want to excpand this caption \n\n-{basic}\n\ninto detailed 30 word desc?"
            try:
                generated=generate_text(prompt_text, max_new_tokens=40)
                description=truncate(generated, 30)
                print(f"{Fore.GREEN} here you go:\n-{Style.BRIGHT}{description}\n")
            except Exception as x:
                print(f"{Fore.RED} sorry, couldnt generate because of {x}\n-")
        elif choice=="3":
            prompt_text=f"do you want to excpand this caption \n\n-{basic}\n\ninto detailed 50 word summary?"
            
            try:
                generate=generate_text(prompt_text, max_new_tokens=60)
                summary=truncate(generated, 50)
                print(f"{Fore.GREEN} here youio go\n\n-{Style.BRIGHT}{summary}\n")
            except Exception as t:
                print(f"{Fore.RED} sorry, couldnt generate because of {t}\n-")
        elif choice=="4":
            print(f"{Fore.GREEN} byeeeee")
            break
        else:
            print("you cant do that, choose an actual number")

if __name__=="__main__":
    main()
