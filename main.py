import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb


data_path = "./dataIn/startup_data.csv"

try:
    df = pd.read_csv(data_path)
    st.success("Fișierul a fost încărcat cu succes!")
except FileNotFoundError:
    st.error("Fișierul CSV nu a fost găsit! Verifică calea sau încarcă un fișier manual.")
    df = None

if df is not None:
    st.title("📊 Analiza Startup-urilor")

    st.markdown("""
    ## 📄 Descrierea Coloanelor:
    - **Startup Name**: Numele startup-ului.
    - **Industry**: Industria în care activează startup-ul (ex: IoT, EdTech, Gaming).
    - **Funding Rounds**: Numărul de runde de finanțare obținute.
    - **Funding Amount (M USD)**: Suma totală de finanțare primită (în milioane USD).
    - **Valuation (M USD)**: Valoarea estimată a startup-ului (în milioane USD).
    - **Revenue (M USD)**: Veniturile generate de startup (în milioane USD).
    - **Employees**: Numărul total de angajați.
    - **Market Share (%)**: Cota de piață deținută de startup.
    - **Profitable**: Indicator binar (1 = profitabil, 0 = neprofitabil).
    - **Year Founded**: Anul în care a fost fondat startup-ul.
    - **Region**: Regiunea în care operează startup-ul.
    - **Exit Status**: Stadiul actual al startup-ului (ex: Privat, Achiziționat).
    """)

    section = st.sidebar.radio("📌 Mergi la:", [
        "Setul de date", "Statistici", "Vizualizare coloana si histograma",
        "Valori Null", "Valori Populare", "Valori Extreme", "Box Plot", "Eliminare Outliers", "Analiza Exploratorie"
    ])

    if section == "Setul de date":
        st.subheader("📂 Setul de date")
        st.dataframe(df)

    elif section == "Statistici":
        st.subheader("📈 Statistici descriptive")
        st.write(df.describe())

    elif section == "Vizualizare coloana si histograma":
        column = st.selectbox("📌 Alege o coloană:", df.columns)
        st.write(f"📊 Statistici pentru: **{column}**")
        st.write(df[column].describe())

        st.subheader("📊 Histograma pentru valoarea aleasa")
        fig, ax = plt.subplots()
        if df[column].dtype in ['int64', 'float64']:
            df[column].hist(ax=ax, bins=20)
            ax.set_xlabel(column)
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
        else:
            st.warning("Această coloana nu este numerică. Alege o a numerica pentru histograma")

    elif section == "Valori Extreme":
        st.subheader("⚠️ Valori extreme (outliers)")
        st.write("🔍 Folosim **IQR (Interquartile Range)** pentru a detecta outliers.")

        df_numeric = df.select_dtypes(include=['number'])

        Q1 = df_numeric.quantile(0.25)
        Q3 = df_numeric.quantile(0.75)
        IQR = Q3 - Q1

        outliers = ((df_numeric < (Q1 - 1.5 * IQR)) | (df_numeric > (Q3 + 1.5 * IQR))).sum()
        st.write(outliers)

    elif section == "Box Plot":
        st.subheader("📦 Box Plot pentru variabile numerice")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            column = st.selectbox("📌 Alege o coloana numerica:", numeric_cols)
            fig, ax = plt.subplots()
            sb.boxplot(y=df[column], ax=ax)
            st.pyplot(fig)
        else:
            st.warning("Nu exista coloane numerice")

    elif section == "Eliminare Outliers":
        st.subheader("🗑️ Eliminare valori extreme folosind IQR")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            column = st.selectbox("📌 Alege o coloana numerică pentru eliminarea outlierilor:", numeric_cols)

            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1

            df_filtered = df[(df[column] >= (Q1 - 1.5 * IQR)) & (df[column] <= (Q3 + 1.5 * IQR))]
            st.write(df_filtered)
        else:
            st.warning("Nu exista coloane numerice pentru eliminarea outlierilor.")

    elif section == "Analiza Exploratorie":
        st.subheader("📊 Analiza Exploratorie a Datelor")
        st.write("✅ **Numar total de randuri si coloane:**", df.shape)
        st.write("✅ **Tipurile de date pentru fiecare coloana:**")
        st.write(df.dtypes)
        st.write("✅ **Distributia valorilor unice:**")
        st.write(df.nunique())

    elif section == "Valori Null":
        st.subheader("❓ Valori lipsa in setul de date")
        missing_values = df.isnull().sum()
        st.write(missing_values[missing_values > 0])

    elif section == "Valori Populare":
        st.subheader("🏆 Cele mai populare valori din fiecare coloană")
        most_common_values = df.mode().iloc[0]
        st.write(most_common_values)

