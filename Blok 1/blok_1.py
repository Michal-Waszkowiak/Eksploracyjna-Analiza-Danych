import pandas as pd
from pandas import IndexSlice
import matplotlib.pyplot as plt
import glob
import sqlite3

def part_I():

    #1. Wczytaj dane ze wszystkich plików do pojedynczej tablicy (używając Pandas).

    data_path = "data/names/"
    data_frame = []

    for file in glob.glob(data_path + "yob*.txt"):
        year = int(file[-8:-4])
        data_frame_ = pd.read_csv(file, names=["Name", "Sex", "Count"])
        data_frame_["Year"] = year
        data_frame.append(data_frame_)

    data = pd.concat(data_frame, ignore_index=True)

    #2. Określi ile różnych (unikalnych) imion zostało nadanych w tym czasie.

    number_unique_names = data["Name"].nunique()
    print(f"Number of unique names: {number_unique_names}")

    #3. Określi ile różnych (unikalnych) imion zostało nadanych w tym czasie rozróżniając imiona męskie i żeńskie.

    number_unique_names_by_sex = data.groupby("Sex")["Name"].nunique()
    print(f"Number of unique names by sex: {number_unique_names_by_sex}")

    #4. Stwórz nowe kolumny frequency_male i frequency_female i określ popularność każdego z imion w danym każdym roku dzieląc liczbę razy,
    #   kiedy imię zostało nadane przez całkowita liczbę urodzeń dla danej płci.

    births_per_year = data.drop(columns=["Name"]).pivot_table(index="Year", columns="Sex", values="Count", aggfunc="sum")
    
    data["frequency_male"] = data["Count"] / data["Year"].map(births_per_year["M"])
    data["frequency_male"] = data["frequency_male"].where(data["Sex"] == "M", 0)

    data["frequency_female"] = data["Count"] / data["Year"].map(births_per_year["F"])
    data["frequency_female"] = data["frequency_female"].where(data["Sex"] == "F", 0)

    print(data)

    #5. Określ i wyświetl wykres złożony z dwóch podwykresów, gdzie osią x jest skala czasu, a oś y reprezentuje:
    #   - liczbę urodzin w danym roku (wykres na górze)
    #   - stosunek liczby narodzin dziewczynek do liczby narodzin chłopców w każdym roku(wykres na dole) W którym roku zanotowano najmniejszą,
    #     a w którym największą różnicę w liczbie urodzeń między chłopcami a dziewczynkami (pytanie dotyczy podwykresu przedstawiającego stosunek liczby urodzin)?
    #     Odpowiedź wyznacz i wyświetl na ekranie

    births_per_year["Factor"] = births_per_year["F"] / births_per_year["M"]
    births_per_year["Diff"] = abs(births_per_year["M"] - births_per_year["F"])

    max_diff = births_per_year["Diff"].idxmax()
    min_diff = births_per_year["Diff"].idxmin()

    print(f"Smallest difference in the number of births: {births_per_year.loc[min_diff, "Diff"]} in {min_diff} year")
    print(f"Biggest difference in the number of births: {births_per_year.loc[max_diff, "Diff"]} in {max_diff} year")
    
    fig, axs = plt.subplots(2,1)
    axs[0].plot(births_per_year.index, births_per_year["M"], label="Boys", color="blue")
    axs[0].plot(births_per_year.index,births_per_year["F"], label="Girls", color="red")
    axs[0].set_title("Number of births by year")
    axs[0].set_xlabel("Year")
    axs[0].set_ylabel("Number of births")
    axs[0].legend()

    axs[1].plot(births_per_year.index, births_per_year["Factor"], label="Girls/Boys", color="black")
    axs[1].set_title("Factor of births by year")
    axs[1].set_xlabel("Year")
    axs[1].set_ylabel("Factor of births")
    axs[1].legend()

    plt.tight_layout()
    # plt.show()

    #6. Wyznacz 1000 najpopularniejszych imion dla każdej płci w całym zakresie czasowym, metoda powinna polegać na wyznaczeniu 1000 najpopularniejszych imion
    #   dla każdego roku i dla każdej płci osobno. Jako najpopularniejsze należy uznać imiona, które najdłużej zajmowały wysokie miejsce na liście rankingowej,
    #   żeby uniknąć wpływu liczny urodzin w danym roku na wynik (liczba urodzin spada stąd, nieprawidłowo przeprowadzona procedura może powodować że imiona nadawane
    #   w wyżu i stosowane w tym czasie zdominują ranking) proszę ranking Top1000 określić jako sumę ważoną względnej popularności danego imienia w danym roku (patrz pkt 4)

    data["Weight_freq"] = data["frequency_male"] + data["frequency_female"]

    weight_sum = data.groupby(["Name", "Sex"])["Weight_freq"].sum().reset_index()

    top_male = (weight_sum[weight_sum["Sex"] == "M"].nlargest(1000, "Weight_freq").reset_index(drop=True))
    top_female = (weight_sum[weight_sum["Sex"] == "F"].nlargest(1000, "Weight_freq").reset_index(drop=True))
    top_1000 = pd.DataFrame({"F": top_female["Name"],
                             "M": top_male["Name"]})

    #7. Wyświetl na jednym wykresie zmiany dla imienia męskiego John i pierwszego imienia żeńskiego rankingu top-1000 (zaopatrz wykres w odpowiednią legendę):
    #   - na osi Y po lewej liczbę razy kiedy imę zostało nadane w każdym roku (wyświetl ile razy nadano to imię w 1934, 1980 i 2022r)?
    #   - na osi Y po prawej popularność tych imion w każdym z tych lat

    male_top1 = "John"
    female_top1 = top_1000.loc[0, "F"]

    # print(female_top1)

    male_top1_data = data[(data["Name"] == male_top1) & (data["Sex"] == "M")]
    female_top1_data = data[(data["Name"] == female_top1) & (data["Sex"] == "F")]
    
    years = [1934, 1980, 2022]

    male_top1_counts = male_top1_data[male_top1_data["Year"].isin(years)]["Count"].tolist()
    male_top1_freq = male_top1_data[male_top1_data["Year"].isin(years)]["frequency_male"].tolist()

    # print(f"Number of name {male_top1} in years {years}: {male_top1_counts}")
    print(f"Number of name {male_top1} in years:")
    print(f"{years[0]} - {male_top1_counts[0]}")
    print(f"{years[1]} - {male_top1_counts[1]}")
    print(f"{years[2]} - {male_top1_counts[2]}")
    # print(f"Popularity of name {male_top1} in years {years}: {male_top1_freq}")
    print(f"Popularity of name {male_top1} in years:")
    print(f"{years[0]} - {male_top1_freq[0]*100} %")
    print(f"{years[1]} - {male_top1_freq[1]*100} %")
    print(f"{years[2]} - {male_top1_freq[2]*100} %")

    female_top1_counts = female_top1_data[female_top1_data["Year"].isin(years)]["Count"].tolist()
    female_top1_freq = female_top1_data[female_top1_data["Year"].isin(years)]["frequency_female"].tolist()

    # print(f"Number of name {female_top1} in years {years}: {female_top1_counts}")
    print(f"Number of name {female_top1} in years:")
    print(f"{years[0]} - {female_top1_counts[0]}")
    print(f"{years[1]} - {female_top1_counts[1]}")
    print(f"{years[2]} - {female_top1_counts[2]}")
    
    # print(f"Popularity of name {female_top1} in years {years}: {female_top1_freq}")
    print(f"Popularity of name {female_top1} in years:")
    print(f"{years[0]} - {female_top1_freq[0]*100} %")
    print(f"{years[1]} - {female_top1_freq[1]*100} %")
    print(f"{years[2]} - {female_top1_freq[2]*100} %")

    fig, ax_left = plt.subplots()
    ax_right = ax_left.twinx()

    ax_left.set_xlabel("Year")
    ax_left.set_ylabel("Count")
    ax_left.plot(male_top1_data["Year"], male_top1_data["Count"], label=f"Count of {male_top1}", color="blue")
    ax_left.plot(female_top1_data["Year"], female_top1_data["Count"], label=f"Count of {female_top1}", color="red")

    ax_right.set_ylabel("Frequency")
    ax_right.plot(male_top1_data["Year"], male_top1_data["frequency_male"], label=f"Frequency of {male_top1}", color="blue", linestyle="--")
    ax_right.plot(female_top1_data["Year"], female_top1_data["frequency_female"], label=f"Frequency of {female_top1}", color="red", linestyle="--")

    fig.legend()
    plt.title(f"Trends for {male_top1} and {female_top1}")
    plt.tight_layout()
    # plt.show()

    #8. Wykreśl wykres z podziałem na lata i płeć zawierający informację jaki procent w danym roku stanowiły imiona należące do rankingu top1000
    #   (wyznaczonego dla całego zbioru (pkt 6)). Wykres ten powinien przedstawiać zmianę różnorodności imion w kolejnych latach z podziałem na płeć.
    #   Zaznacz na wykresie oraz wyświetl w konsoli rok, w którym zaobserwowano największą różnicę w różnorodności między imionami męskimi a żeńskimi.
    #   Odpowiedz na pytanie wyświetlając odpowiedni tekst w skrypcie: "Co zmieniło się na przestrzeni ostatnich 140 lat jeśli chodzi o różnorodność imion?
    #   czy różnorodność zależy od płci?"

    top1000_names = set(top_1000["F"]).union(set(top_1000["M"]))
    data["is_top1000"] = data["Name"].isin(top1000_names)

    top1000_perc_by_year = data[data["is_top1000"]].pivot_table(index="Year", columns="Sex", values="Count", aggfunc="sum")
    top1000_perc = top1000_perc_by_year / births_per_year.drop(columns=["Diff", "Factor"]) * 100
    top1000_perc["Diff"] = abs(top1000_perc["M"] - top1000_perc["F"])
    top1000_perc_max_diff = top1000_perc["Diff"].idxmax()

    print(f"Year with the largest diversity difference - {top1000_perc_max_diff}")
    print(f"Male names - {top1000_perc.loc[top1000_perc_max_diff, "M"]} %")
    print(f"Female names - {top1000_perc.loc[top1000_perc_max_diff, "F"]} %")
    print(f"Difference - {abs(top1000_perc.loc[top1000_perc_max_diff, "F"] - top1000_perc.loc[top1000_perc_max_diff, "M"])} %")

    fig, ax = plt.subplots()
    ax.plot(top1000_perc.index, top1000_perc["M"], label="Male top 1000", color="blue")
    ax.plot(top1000_perc.index, top1000_perc["F"], label="Female top 1000", color="red")
    ax.axvline(top1000_perc_max_diff, color="black", linestyle="--", label=f"Max difference ({top1000_perc_max_diff})")

    ax.set_title("Diversity of top 1000 names by sex over time")
    ax.set_xlabel("Year")
    ax.set_ylabel(f"% of top 1000 names")
    ax.legend()
    plt.tight_layout()
    # plt.show()

    # Co zmieniło się na przestrzeni ostatnich 140 lat jeśli chodzi o różnorodność imion?
    # czy różnorodność zależy od płci?"
    #
    # Na przestrzeni ostatnich 140 lat można zauważyć, że różnorodność imion w Ameryce zarówno w przypadku dziewczyn jak i w przypadku chłopców uległa mocno zmianie.
    # Jak jeszcze powiedzmy do roku 1960 nie obserwujemy znaczących zmian, to już po tym roku widać, że procent najpopularniejszych imion znacznie spada. Czy różnorodność zależy od płci?
    # Tak, widać, że wśród dziewczyn dochodzi do większego urozmaicenia imion niż w przypadku chłopców, jednak w obu przypadkach ta tendencja idzie w tym samym kierunku.
    # (Zapytać się czy mam podać jakiś punkt zwrotny w historii USA)

    #9. Zweryfikuj hipotezę czy prawdą jest, że w obserwowanym okresie rozkład ostatnich liter imion męskich uległ istotnej zmianie? W tym celu
    #   - dokonaj agregacji wszystkich urodzeń w pełnym zbiorze danych z podziałem na rok i płeć i ostatnią literę,
    #   - wyodrębnij dane dla lat 1910, 1970, 2023
    #   - znormalizuj dane względem całkowitej liczby urodzin w danym roku
    #   - wyświetl dane popularności litery dla mężczyzn w postaci wykresu słupkowego zawierającego poszczególne lata i gdzie słupki grupowane są wg litery.
    #     Wyświetl, dla której litery wystąpił największy wzrost/spadek między rokiem 1910 a 2023)
    #   - Dla 3 liter dla których zaobserwowano największą zmianę wyświetl przebieg trendu popularności w całym okresie czasu

    male_data = data[data["Sex"] == "M"]
    male_data["Last_letter"] = male_data["Name"].str[-1]

    last_letter_pivot = male_data.drop(columns=["Name", "frequency_male", "frequency_female",
                                           "Weight_freq", "is_top1000"]).pivot_table(index="Last_letter", columns=["Year", "Sex"], values="Count",
                                                                                     aggfunc="sum", fill_value=0)

    years_ = [1910, 1970, 2023]


    norm_male_last_letter_data = last_letter_pivot.loc[:, (years_, "M")].div(births_per_year.loc[years_, "M"].values, axis=1)
    norm_male_last_letter_data.columns = years_
    norm_male_last_letter_data.plot(kind="bar")
    plt.title("Normalized popularity of last letters in male names")
    plt.xlabel("Last Letter")
    plt.ylabel("Normalized Frequency")
    plt.legend(title="Year")
    plt.tight_layout()
    # plt.show()

    norm_male_last_letter_data["1910-2023"] = norm_male_last_letter_data[2023] - norm_male_last_letter_data[1910]

    top1_increase = norm_male_last_letter_data["1910-2023"].nlargest(1)
    top1_decrease = norm_male_last_letter_data["1910-2023"].nsmallest(1)

    print(f"Largest increase between 1910 - 2023: {top1_increase}")
    print(f"Largest decrease between 1910 - 2023: {top1_decrease}")

    norm_male_last_letter_data["abs_1910-2023"] = norm_male_last_letter_data["1910-2023"].abs()

    sorted_last_letter_data = norm_male_last_letter_data.sort_values(by="abs_1910-2023", ascending=False)

    top3_letters = sorted_last_letter_data["abs_1910-2023"].nlargest(3).index

    selected_letters_data = last_letter_pivot.loc[top3_letters]

    norm_selected_letters_data = selected_letters_data.div(births_per_year["M"].values, axis=1)
    norm_selected_letters_data.columns = norm_selected_letters_data.columns.get_level_values(0)


    fig, ax = plt.subplots()

    for letter in top3_letters:
        ax.plot(norm_selected_letters_data.loc[letter].index, norm_selected_letters_data.loc[letter], label=f"Letter: {letter}")

    ax.set_xlabel("Year")
    ax.set_ylabel("Normalized Frequency")
    ax.set_title("Trend of last letters with largest difference")
    ax.legend()
    plt.tight_layout()
    # plt.show()

    #10. Znajdź w rankingu top1000 imiona, które nadawane były zarówno dziewczynkom jak i chłopcom (stosunek nadanych imion męskich i żeńskich).
    #    Wyznacz 2 imiona (jedno które z kiedyś było typowo męskie a aktualnie jest imieniem żeńskim i drugie które kiedyś było typowo żeńskim a
    #    aktualnie jest typowo męskim). Typowo męskie imię to takie dla którego iloraz imion nadawanych chłopcom do całkowitej liczby imion jest bliski 1 (p_m),
    #    analogicznie iloraz można zdefiniować dla dziewczynek (p_k). Największa zmiana między rokiem X a rokiem Y może być zdefiniowana jako średnia z sumy (p_m(X)+p_k(Y))/2.
    #    Do analizy zmiany konotacji imienia wykorzystaj 2 przedziały: zagregowane dane do roku 1920 i od roku 2000.
    #    - wyświetl te imiona
    #    - wkreśl przebieg trendu dla tych imion obrazujący zmianę konotacji danego imienia na przestrzeni lat

    same_names = set(top_female["Name"]).intersection(set(top_male["Name"]))
    print(f"Liczba imion wspólnych dla płci: {len(same_names)}")

    same_names_data = data[data["Name"].isin(same_names)]
    same_names_stats = same_names_data.pivot_table(index=["Name", "Year"], columns="Sex", values="Count", aggfunc="sum", fill_value=0)
    same_names_stats['ratio_male_to_female'] = same_names_stats['M'] / same_names_stats['F']
    same_names_stats['p_m'] = same_names_stats['M'] / (same_names_stats['M'] + same_names_stats['F'])
    same_names_stats['p_k'] = same_names_stats['F'] / (same_names_stats['M'] + same_names_stats['F'])

    data_1920 = same_names_stats[same_names_stats.index.get_level_values('Year') <= 1920]
    data_2000 = same_names_stats[same_names_stats.index.get_level_values('Year') >= 2000]

    change_stats = data_1920.groupby('Name')['p_m'].mean().to_frame(name='p_m')
    change_stats['p_k_1920'] = data_1920.groupby('Name')['p_k'].mean()
    change_stats['p_m_2000'] = data_2000.groupby('Name')['p_m'].mean()
    change_stats['p_k'] = data_2000.groupby('Name')['p_k'].mean()
    change_stats.rename(columns={'p_m': 'p_m_1920', 'p_k': 'p_k_2000'}, inplace=True)
    
    

    change_stats['change_m_k'] = (change_stats['p_m_1920'] + change_stats['p_k_2000']) / 2
    change_stats['change_k_m'] = (change_stats['p_k_1920'] + change_stats['p_m_2000']) / 2

    # print(same_names_stats.head(1000))
    # print(data_1920)
    # print(data_2000)
    # pd.set_option('display.max_rows', None)
    # print(change_stats)

    max_change_name_mk = change_stats['change_m_k'].idxmax()
    max_change_value_mk = change_stats['change_m_k'].max()

    max_change_name_km = change_stats['change_k_m'].idxmax()
    max_change_value_km = change_stats['change_k_m'].max()

    print(f"Name: Man -> Woman: {max_change_name_mk} \n Connotation: {max_change_value_mk}")
    print(f"Name: Woman -> Man: {max_change_name_km} \n Connotation: {max_change_value_km}")

    max_change_name_data_mk = same_names_stats.loc[max_change_name_mk]
    max_change_name_data_km = same_names_stats.loc[max_change_name_km]

    fig, axs = plt.subplots(2,1)
    axs[0].plot(max_change_name_data_mk.index.get_level_values('Year'), max_change_name_data_mk['p_m'], label='p_m (Boys)', color='blue')
    axs[0].plot(max_change_name_data_mk.index.get_level_values('Year'), max_change_name_data_mk['p_k'], label='p_k (Girls)', color='red')
    axs[0].set_title(f"Change connotation of name '{max_change_name_mk}' over the years")
    axs[0].set_xlabel("Year")
    axs[0].set_ylabel("Ratio")
    axs[0].legend()

    axs[1].plot(max_change_name_data_km.index.get_level_values('Year'), max_change_name_data_km['p_m'], label='p_m (Boys)', color='green')
    axs[1].plot(max_change_name_data_km.index.get_level_values('Year'), max_change_name_data_km['p_k'], label='p_k (Girls)', color='magenta')
    axs[1].set_title(f"Change connotation of name '{max_change_name_km}' over the years")
    axs[1].set_xlabel("Year")
    axs[1].set_ylabel("Ratio")
    axs[1].legend()
    plt.tight_layout()
    plt.show()

def part_II():
    conn = sqlite3.connect("data/names_pl_2000-23.sqlite")

    query = """
    SELECT 'F' AS Sex, Imię AS Name, Rok AS Year, Liczba AS Count
    FROM females
    WHERE Rok BETWEEN 2000 AND 2023

    UNION ALL

    SELECT 'M' AS Sex, Imię AS Name, Rok AS Year, Liczba AS Count
    FROM males
    WHERE Rok BETWEEN 2000 AND 2023;
    """

    data = pd.read_sql_query(query, conn)
    conn.close()
    # print(df)

    births_per_year = data.drop(columns=["Name"]).pivot_table(index="Year", columns="Sex", values="Count", aggfunc="sum")
    
    data["frequency_male"] = data["Count"] / data["Year"].map(births_per_year["M"])
    data["frequency_male"] = data["frequency_male"].where(data["Sex"] == "M", 0)

    data["frequency_female"] = data["Count"] / data["Year"].map(births_per_year["F"])
    data["frequency_female"] = data["frequency_female"].where(data["Sex"] == "F", 0)

    data["Weight_freq"] = data["frequency_male"] + data["frequency_female"]

    weight_sum = data.groupby(["Name", "Sex"])["Weight_freq"].sum().reset_index()

    top_male = (weight_sum[weight_sum["Sex"] == "M"].nlargest(200, "Weight_freq").reset_index(drop=True))
    top_female = (weight_sum[weight_sum["Sex"] == "F"].nlargest(200, "Weight_freq").reset_index(drop=True))
    top_200 = pd.DataFrame({"F": top_female["Name"],
                             "M": top_male["Name"]})
    
    # print(top_200)

    top200_names = set(top_200["F"]).union(set(top_200["M"]))
    data["is_top200"] = data["Name"].isin(top200_names)

    top200_perc_by_year = data[data["is_top200"]].pivot_table(index="Year", columns="Sex", values="Count", aggfunc="sum")
    top200_perc = top200_perc_by_year / births_per_year * 100
    top200_perc["Diff"] = abs(top200_perc["M"] - top200_perc["F"])
    top200_perc_max_diff = top200_perc["Diff"].idxmax()

    print(f"Year with the largest diversity difference - {top200_perc_max_diff}")
    print(f"Male names - {top200_perc.loc[top200_perc_max_diff, "M"]} %")
    print(f"Female names - {top200_perc.loc[top200_perc_max_diff, "F"]} %")
    print(f"Difference - {abs(top200_perc.loc[top200_perc_max_diff, "F"] - top200_perc.loc[top200_perc_max_diff, "M"])} %")

    # W USA najwięszką różnicę odnotowano w 2008 i wyniosła ona 15.93%, natomiast w Polsce był to rok 2000 na poziomie 0.69%
    # Można zatem zauważyć, że w Polsce nie doszło do takiej różnorodności

    fig, ax = plt.subplots()
    ax.plot(top200_perc.index, top200_perc["M"], label="Male top 200", color="blue")
    ax.plot(top200_perc.index, top200_perc["F"], label="Female top 200", color="red")
    ax.axvline(top200_perc_max_diff, color="black", linestyle="--", label=f"Max difference ({top200_perc_max_diff})")

    ax.set_title("Diversity of top 200 names by sex over time")
    ax.set_xlabel("Year")
    ax.set_ylabel(f"% of top 200 names")
    ax.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # part_I()
    part_II()