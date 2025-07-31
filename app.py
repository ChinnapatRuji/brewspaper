import app_functions as af
import streamlit as st

def main():
    st.session_state.vector_db = af.get_vector()
    st.set_page_config(
        page_title = "Brewspaper",
        page_icon = ":newspaper:"
    )
    st.header("Get any news topic you want")
    # if st.button("Load News"):
    #     with st.spinner("Loading..."):
    #         if "vector_db" in st.session_state:
    #             del st.session_state["vector_db"]
    #         try:
    #             df = af.get_news("feeds.json")
    #             st.session_state.vector_db = af.get_vector(df)
    #             st.success("Loading Complete")
    #         except:
    #             st.write("Loading Failed. Try Again") 
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