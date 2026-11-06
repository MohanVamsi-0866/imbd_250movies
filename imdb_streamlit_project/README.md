# IMDb Movie Analytics Dashboard (Streamlit)

A dark, responsive movie analytics dashboard inspired by the supplied reference image and built to cover the tasks in the Streamlit Practical Examination question paper.

## Included features

- CSV upload in the sidebar (or automatic loading of `Top 250 movies on imdb in 2026.csv` when placed beside `app.py`).
- First 10 records, row/column counts, column names, data types and missing-value counts.
- Four KPI metrics: total movies, average IMDb rating, highest rating and total votes.
- Genre bar chart, IMDb rating histogram, rating-votes scatter plot and top-10 worldwide-gross chart.
- Separate visualization tabs and expandable dataset information.
- Interactive explorer: genre, countries, rating range, minimum votes, title search, rating sort and reset.
- Movie search form using `st.form`, `st.form_submit_button` and `st.session_state`.
- Responsive dark styling and Plotly charts.

## Run locally (Mac / Windows)

1. Extract the ZIP file.
2. Open the extracted `imdb_streamlit_project` folder in VS Code or Terminal.
3. Create and activate a virtual environment (recommended):

   **Mac:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   **Windows:**
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

4. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the dashboard:
   ```bash
   streamlit run app.py
   ```
6. A browser tab opens. Upload your IMDb CSV using the sidebar uploader if it is not already beside `app.py`.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `README.md`.
2. Do **not** commit a private or restricted dataset. If the dataset is permitted for public hosting, you may include the CSV in the repository; otherwise leave it out and use the app's CSV uploader.
3. Visit https://share.streamlit.io/ and sign in with GitHub.
4. Select **Create app**, choose your repository, branch (usually `main`) and main file path `app.py`.
5. Select **Deploy**. Streamlit installs packages from `requirements.txt` and publishes your app.
6. Open the generated `*.streamlit.app` URL to test the deployed dashboard.

## Dataset columns

The app detects common variants of these fields: title/movie, genres/genre, country/countries, `averageRating`, `numVotes`, and `grossWorldwide`. If your CSV uses different names, the dashboard still loads where possible; unavailable charts show a helpful note.
