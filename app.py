from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import urllib.request
import numpy as np
#import pickle
from PIL import Image
import base64
from io import BytesIO

app = Flask(__name__)

def starR(n):
    if n % 1 < 0.5:
        return int(n // 1) * "⭐"
    else:
        return (int(n // 1) + 1) * "⭐"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # with open('results.pkl', 'rb') as f:
    #     results = pickle.load(f)
    #     return render_template('results.html', results=results)
    product = request.form['product']
    if product == "":
        return "Please Enter Something!!"
    else:
         
        try:
            HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
            response = requests.get(f"https://www.amazon.in/s?k={product}", headers=HEADERS)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            return f"HTTP Error: {errh}"
        except requests.exceptions.ConnectionError as errc:
            return f"Error Connecting: {errc}"
        except requests.exceptions.Timeout as errt:
            return f"Timeout Error: {errt}"
        except requests.exceptions.RequestException as err:
            return f"Something went wrong: {err}"

        soup = BeautifulSoup(response.content, "html.parser")
        dibba = soup.findAll("div", {"class": "a-section a-spacing-small a-spacing-top-small"})
        bigdibba = soup.findAll("div", {"class": "a-section aok-relative s-image-fixed-height"})
        if len(dibba) > 0:
            dibba.pop(0)
            results = []
            for i in range(len(dibba)):
                n = dibba[i].find("span", {"class": "a-size-medium a-color-base a-text-normal"})
                name = n.get_text() if n else "NA"

                p = dibba[i].find("span", {"class": "a-offscreen"})
                price = p.get_text() if p else "NA"

                r = dibba[i].find("span", {"class": "a-icon-alt"})
                if r:
                    rn = float(r.get_text()[:3])
                    r = starR(rn)
                else:
                    r = "NA"
                    rn = None

                rw = dibba[i].find("span", {"class": "a-size-base s-underline-text"})
                reviews = rw.get_text() if rw else "NA"

                bl = dibba[i].find("a", {"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})
                if bl:
                    l = bl.get("href")
                    if l:
                        bl = "https://www.amazon.in" + l

                image = bigdibba[i].find("img", {"class": "s-image"})
                if image:
                    img_url = image.get("src")
                    try:
                        with urllib.request.urlopen(img_url) as response:
                            if response.status == 200:
                                img_data = np.array(Image.open(response))
                                pil_img = Image.fromarray(img_str)
                                buffered = BytesIO()
                                pil_img.save(buffered, format="JPEG")
                                img_str = base64.b64encode(buffered.getvalue()).decode()
                                results.append({
                                    'image': img_data,
                                    'name': name,
                                    'price': price,
                                    'rating': r,
                                    'reviews': reviews,
                                    'link': bl
                                })
                    except Exception as e:
                        print(f"Error: {e}\nFailed to open the image URL.")
                else:
                    results.append({
                        'image': None,
                        'name': name,
                        'price': price,
                        'rating': r,
                        'reviews': reviews,
                        'link': bl
                    })

            return render_template('results.html', results=results)
        else:
            return "No Results found"
        
if __name__ == '__main__':
    app.run(debug=True)

 
