import app_functions as af
import streamlit as st

def main():
    st.session_state.vector_db = af.get_vector()
    st.set_page_config(
        page_title = "Brewspaper",
        page_icon = ":newspaper:"
    )
    st.header("Get any news topic you want")
    query = st.text_input("News topic")
    if st.button("Enter"):
        try:
            with st.spinner("Searching..."):
                vector_db = st.session_state.get("vector_db")
                context = af.get_context(vector_db, query)
                st.subheader("News")
                ans = af.ask_gemini_pick_best_news(context, query)
                st.text(ans)
        except:
            st.error("Error")

if __name__ == "__main__":
    main()