import requests


def call0():
    url = "http://0.0.0.0:8080/generate-tiles-from-random-chessboard"

    response = requests.get(url)

    if response.status_code == 200:
        with open("downloaded_file.zip", "wb") as file:
            file.write(response.content)
        print("file downloaded successfully")
    else:
        print("error occured!")


if __name__ == "__main__":
    call0()
