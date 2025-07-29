

def main():
    api_key = "your_api_key"
    gan_api = GanAPI(api_key)
    print(gan_api.ping())
    
if __name__ == "__main__":
    main()