import app_functions as af

def main():
    df = af.get_news("feeds.json")
    af.get_vector_chroma(df)

if __name__ == "__main__":
    main()