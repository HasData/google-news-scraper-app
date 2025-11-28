import streamlit as st
import requests
import json
import pandas as pd
import io

st.set_page_config(page_title="Google News Scraper", layout="wide")
st.markdown("<h1 style='text-align: center;'>Google News Scraping with HasData API</h1>", unsafe_allow_html=True)

api_key = st.text_input("Enter your HasData's API Key", placeholder="Your API Key here")

st.subheader("Query Parameters")
col1, col2 = st.columns(2, gap="small")

with col1:
    q = st.text_input("Free-text Query (q)", "")

    topics = [
        {"title":"U.S.","topicToken":"CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE"},
        {"title":"World","topicToken":"CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB"},
        {"title":"Local","topicToken":"CAAqHAgKIhZDQklTQ2pvSWJHOWpZV3hmZGpJb0FBUAE"},
        {"title":"Business","topicToken":"CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB"},
        {"title":"Technology","topicToken":"CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB"},
        {"title":"Entertainment","topicToken":"CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB"},
        {"title":"Sports","topicToken":"CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB"},
        {"title":"Science","topicToken":"CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB"},
        {"title":"Health","topicToken":"CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ"}
    ]

    topic_titles = [t["title"] for t in topics] + ["Custom"]
    topic_choice = st.selectbox("Topic Token", topic_titles, index=1)

    if topic_choice == "Custom":
        topicToken = st.text_input("Enter your custom TopicToken", "")
    else:
        topicToken = next((t["topicToken"] for t in topics if t["title"] == topic_choice), "")

    sectionToken = st.text_input("Section Token", "")
    publicationToken = st.text_input("Publication Token", "")

with col2:
    storyToken = st.text_input("Story Token", "")
    country_map = {"USA":"us","United Kingdom":"uk","Germany":"de","France":"fr","India":"in","Canada":"ca","Australia":"au"}
    country_name = st.selectbox("Country (gl)", list(country_map.keys()), index=0)
    gl = country_map[country_name]

    language_map = {"English (US)":"en","English (UK)":"en-gb","German":"de","French":"fr","Spanish":"es","Hindi":"hi"}
    language_name = st.selectbox("Language (hl)", list(language_map.keys()), index=0)
    hl = language_map[language_name]

    sort_map = {"Relevance":0, "Date":1}
    so_name = st.selectbox("Sort Order (so)", list(sort_map.keys()), index=0)
    so = sort_map[so_name]

raw_params = {"q":q,"gl":gl,"hl":hl,"topicToken":topicToken,"sectionToken":sectionToken,
              "publicationToken":publicationToken,"storyToken":storyToken,"so":so}
params = {k:v for k,v in raw_params.items() if v}

if "rows" not in st.session_state:
    st.session_state.rows = None

if st.button("Scrape News"):
    if not api_key:
        st.error("API Key is required.")
    else:
        headers = {"Content-Type":"application/json","x-api-key":api_key}
        url = "https://api.hasdata.com/scrape/google/news"

        try:
            resp = requests.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

        rows = []
        for item in data.get("newsResults", []):
            h = item.get("highlight", {})
            s = h.get("source", {})
            rows.append({
                "position": item.get("position"),
                "title": h.get("title"),
                "link": h.get("link"),
                "date": h.get("date"),
                "thumbnail": h.get("thumbnail"),
                "thumbnailSmall": h.get("thumbnailSmall"),
                "source_name": s.get("name"),
                "source_icon": s.get("icon"),
                "source_authors": ", ".join(s.get("authors", [])),
                "stories_json": json.dumps(item.get("stories", []), ensure_ascii=False)
            })

        st.session_state.rows = rows

rows = st.session_state.rows

if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df, width='stretch')
    json_data = json.dumps(rows, ensure_ascii=False, indent=2)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Download JSON", data=json_data, file_name="news.json", mime="application/json")
    with c2:
        st.download_button("Download CSV", data=csv_buffer.getvalue(), file_name="news.csv", mime="text/csv")
else:
    st.info("Enter parameters and press **Scrape News**.")

