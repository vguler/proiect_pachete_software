import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import geopandas as gpd
from shapely.geometry.point import Point
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm

data_path = "./dataIn/startup_data.csv"

try:
    df = pd.read_csv(data_path)
    st.success("Fisierul a fost incarcat cu succes!")
except FileNotFoundError:
    st.error("Fisierul CSV nu a fost gasit! Verifica calea sau incarca un fisier manual.")
    df = None

if df is not None:
    st.title("📊 Analiza Startup-urilor")

    section = st.sidebar.radio("📌 Meniu:", [
        "Setul de date", "Statistici", "Vizualizare coloana si histograma",
        "Valori Null", "Valori Populare", "Valori Extreme", "Box Plot",
        "Eliminare Outliers", "Analiza Exploratorie", "Codificare date",
        "Scalare date", "GroupBy", "Clusterizare", "Regresie Logistica",
        "Regresie Multipla", "Harta (geopandas)"
    ])

    if section == "Setul de date":
        st.subheader("Setul de date")
        st.dataframe(df)

    elif section == "Statistici":
        st.subheader("Statistici descriptive")
        st.write(df.describe())

    elif section == "Vizualizare coloana si histograma":
        column = st.selectbox("Alege o coloana:", df.columns)
        st.write(f"Statistici pentru: {column}")
        st.write(df[column].describe())

        st.subheader("Histograma")
        fig, ax = plt.subplots()
        if df[column].dtype in ['int64', 'float64']:
            df[column].hist(ax=ax, bins=20)
            ax.set_xlabel(column)
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
        else:
            st.warning("Coloana nu este numerica.")

    elif section == "Valori Null":
        st.subheader("Valori lipsa")
        missing = df.isnull().sum()
        st.write(missing[missing > 0])

    elif section == "Valori Populare":
        st.subheader("Valori cele mai frecvente")
        st.write(df.mode().iloc[0])

    elif section == "Valori Extreme":
        st.subheader("Valori extreme (IQR)")
        df_numeric = df.select_dtypes(include=['number'])
        Q1 = df_numeric.quantile(0.25)
        Q3 = df_numeric.quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df_numeric < (Q1 - 1.5 * IQR)) | (df_numeric > (Q3 + 1.5 * IQR))).sum()
        st.write(outliers)

    elif section == "Box Plot":
        st.subheader("Box Plot")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            column = st.selectbox("Alege o coloana:", numeric_cols)
            fig, ax = plt.subplots()
            sb.boxplot(y=df[column], ax=ax)
            st.pyplot(fig)

    elif section == "Eliminare Outliers":
        st.subheader("Eliminare outliers (IQR)")
        column = st.selectbox("Alege o coloana:", df.select_dtypes(include=['number']).columns)
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        df_filtered = df[(df[column] >= (Q1 - 1.5 * IQR)) & (df[column] <= (Q3 + 1.5 * IQR))]
        st.write(df_filtered)

    elif section == "Analiza Exploratorie":
        st.subheader("Analiza exploratorie")
        st.write("Dimensiune:", df.shape)
        st.write("Tipuri de date:")
        st.write(df.dtypes)
        st.write("Numar valori unice:")
        st.write(df.nunique())

    elif section == "Codificare date":
        st.subheader("Codificare cu LabelEncoder")
        cat_cols = df.select_dtypes(include=['object']).columns
        column = st.selectbox("Alege coloana categorica:", cat_cols)
        le = LabelEncoder()
        df[f"{column}_encoded"] = le.fit_transform(df[column])
        st.write(df[[column, f"{column}_encoded"]])

    elif section == "Scalare date":
        st.subheader("Scalare cu MinMaxScaler")
        col = st.selectbox("Alege coloana numerica:", df.select_dtypes(include=['number']).columns)
        scaler = MinMaxScaler()
        df[f"{col}_scaled"] = scaler.fit_transform(df[[col]])
        st.write(df[[col, f"{col}_scaled"]])

    elif section == "GroupBy":
        st.subheader("GroupBy pe regiune")
        if "Region" in df.columns:
            grouped = df.groupby("Region")["Revenue (M USD)"].sum().reset_index()
            st.write(grouped)
        else:
            st.warning("Coloana 'Region' nu exista.")

    elif section == "Clusterizare":
        st.subheader("Clusterizare KMeans")
        cols = st.multiselect("Alege coloane numerice:", df.select_dtypes(include=['number']).columns)
        if len(cols) >= 2:
            k = st.slider("Numar de clustere:", 2, 6, 3)
            model = KMeans(n_clusters=k)
            df["Cluster"] = model.fit_predict(df[cols])
            st.write(df[["Cluster"] + cols])

    elif section == "Regresie Logistica":
        st.subheader("Regresie logistica (Profitable)")
        cols = st.multiselect("Coloane predictori:", df.select_dtypes(include=['number']).columns.drop("Profitable"))
        if cols:
            X = df[cols]
            y = df["Profitable"]
            model = LogisticRegression()
            model.fit(X, y)
            st.write("Coeficienti:", model.coef_)
            st.write("Intercept:", model.intercept_)

    elif section == "Regresie Multipla":
        st.subheader("Regresie multipla (Valuation)")
        cols = st.multiselect("Predictori:", ["Revenue (M USD)", "Employees"])
        if "Valuation (M USD)" in df.columns and all(col in df.columns for col in cols):
            X = df[cols]
            X = sm.add_constant(X)
            y = df["Valuation (M USD)"]
            model = sm.OLS(y, X).fit()
            st.write(model.summary())

    elif section == "Harta (geopandas)":
        st.subheader("Harta Startup-urilor pe Regiuni")

        try:


            region_coords = {
                "Europe": (50.1109, 8.6821),         # Frankfurt
                "North America": (37.7749, -122.4194), # San Francisco
                "South America": (-23.5505, -46.6333), # Sao Paulo
                "Asia": (35.6895, 139.6917),          # Tokyo
                "Australia": (-33.8688, 151.2093),    # Sydney
            }

            if "Region" not in df.columns:
                st.error("Coloana 'Region' nu exista in setul de date.")
            else:
                df['Latitude'] = df['Region'].map(lambda x: region_coords.get(x, (0, 0))[0])
                df['Longitude'] = df['Region'].map(lambda x: region_coords.get(x, (0, 0))[1])
                map_df = df[['Latitude', 'Longitude']].copy()
                map_df = map_df.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
                st.map(map_df)

        except Exception as e:
            st.error(f"Nu s-a putut incarca harta: {e}")




