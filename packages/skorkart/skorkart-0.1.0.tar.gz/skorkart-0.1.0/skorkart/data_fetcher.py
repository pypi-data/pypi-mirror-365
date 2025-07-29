import time
import pandas as pd
from io import StringIO
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from .setup_webdriver import setup_webdriver
from .utils import (
    TABS,
    previous_period,
    period_regex,
    get_localized_message,
    format_period,
)

def scorecard_data(
    stock_codes: list[str] | str,
    start_period: str,
    end_period: str,
    lang: str = "tr",
    save_to_excel: bool = False,
    merge_to_single_excel: bool = True,
    wait_seconds: float = 3,
    financials: bool = True,
    profitability: bool = True,
    multiples: bool = True,
) -> dict[str, dict[str, pd.DataFrame]]:
    """
    Fetches scorecard data for given stock codes and periods, saves as Excel if requested.

    Args:
        stock_codes (list[str] | str): List of stock codes or a single stock code.
        start_period (str): Starting period, e.g. '2019/12'.
        end_period (str): Ending period, e.g. '2025/03'.
        lang (str, optional): Language for messages ('tr' or 'en'). Defaults to 'tr'.
        save_to_excel (bool, optional): Whether to save dataframes as Excel files. Defaults to False.
        merge_to_single_excel (bool, optional): If True, writes all stocks to a single Excel file with a sheet per stock. If False, writes each stock to a separate Excel file. Defaults to True.
        wait_seconds (float, optional): Seconds to wait for loading between actions. Defaults to 3.
        financials (bool, optional): If True, fetch 'Financials' table.
        profitability (bool, optional): If True, fetch 'Profitability' table.
        multiples (bool, optional): If True, fetch 'Multiples' table.

    Returns:
        dict[str, dict[str, pd.DataFrame]]:
            Dictionary with table names as keys (e.g. "Financials"), and for each, a dict mapping stock codes to DataFrames.
            Example: results["Financials"]["THYAO"]
    """
    wait_seconds = max(3, float(wait_seconds))
    if isinstance(stock_codes, str):
        stock_codes = [stock_codes]

    try:
        start_period = format_period(start_period, lang)
        end_period = format_period(end_period, lang)
    except ValueError as e:
        print(e)
        return {}

    tab_choices = []
    if financials:
        tab_choices.append("Financials")
    if profitability:
        tab_choices.append("Profitability")
    if multiples:
        tab_choices.append("Multiples")
    filtered_tabs = [tab for tab in TABS if tab["name"] in tab_choices]

    tables = {tab['name']: {} for tab in filtered_tabs}

    for stock_code in stock_codes:
        driver, wait = setup_webdriver(lang)
        url = f"https://analizim.halkyatirim.com.tr/Financial/ScoreCardDetail?hisseKod={stock_code}"
        driver.get(url)
        time.sleep(wait_seconds)

        period = end_period
        temp_tables = {tab['name']: pd.DataFrame() for tab in filtered_tabs}
        stock_invalid = False

        try:
            while True:
                try:
                    select_elem = wait.until(
                        lambda d: d.find_element("id", "seciliHisseDonem")
                    )
                except TimeoutException:
                    print(get_localized_message("stock_not_found", lang, stock_code))
                    stock_invalid = True
                    break

                select = Select(select_elem)
                try:
                    select.select_by_visible_text(period)
                except Exception:
                    print(get_localized_message("period_not_found", lang, period, stock_code))
                    period = previous_period(period)
                    if period < start_period:
                        stock_invalid = True
                        break
                    continue
                time.sleep(wait_seconds)
                refresh_btn = wait.until(lambda d: d.find_element("id", "btnRefresh"))
                refresh_btn.click()
                time.sleep(wait_seconds)

                for tab in filtered_tabs:
                    tab_element = wait.until(
                        lambda d: d.find_element("css selector", f'a[href="{tab["tab_href"]}"]')
                    )
                    tab_element.click()
                    time.sleep(wait_seconds)
                    table = wait.until(
                        lambda d: d.find_element("css selector", f'div#{tab["tab_id"]} table')
                    )
                    html = table.get_attribute('outerHTML')
                    df = pd.read_html(StringIO(html), header=0)[0]

                    first_col = df.columns[0]
                    if stock_code in str(first_col) or "Tarih" not in str(first_col):
                        df.columns = ['Tarih'] + list(df.columns[1:])
                    df['Hisse Adı'] = stock_code

                    temp_tables[tab['name']] = pd.concat([temp_tables[tab['name']], df], ignore_index=True)

                all_periods = temp_tables[filtered_tabs[0]['name']].iloc[:, 0].astype(str)
                valid_periods = [d for d in all_periods if period_regex.match(d)]
                if start_period in valid_periods:
                    break
                if valid_periods:
                    last_period = valid_periods[-1]
                else:
                    print(get_localized_message("no_valid_period", lang, stock_code))
                    break
                if last_period == period or last_period < start_period:
                    break
                period = previous_period(last_period)

            if stock_invalid:
                continue

            for name in temp_tables:
                df = temp_tables[name]
                if "Tarih" not in df.columns:
                    continue
                df = df[df['Tarih'].astype(str).str.match(period_regex)]
                df = df[df['Tarih'].astype(str) >= start_period]
                df = df[df['Tarih'].astype(str) <= end_period]
                df = df.drop_duplicates()
                tables[name][stock_code] = df

            print(get_localized_message("stock_done", lang, stock_code))

        except TimeoutException:
            print(get_localized_message("stock_not_found", lang, stock_code))
            continue
        finally:
            driver.quit()

    for name, stock_dfs in tables.items():
        if not stock_dfs:
            continue
        if save_to_excel:
            if merge_to_single_excel:
                filename = f"{name.lower()}_{start_period.replace('/','')}_{end_period.replace('/','')}.xlsx"
                with pd.ExcelWriter(filename, engine="openpyxl") as writer:
                    for stock_code, df in stock_dfs.items():
                        sheet_name = stock_code[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(get_localized_message("saved_excel", lang, filename))
            else:
                for stock_code, df in stock_dfs.items():
                    filename = f"{name.lower()}_{stock_code}_{start_period.replace('/','')}_{end_period.replace('/','')}.xlsx"
                    df.to_excel(filename, index=False)
                    print(get_localized_message("saved_excel", lang, filename))

    print(get_localized_message("all_done", lang))
    return tables