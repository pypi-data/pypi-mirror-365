# skorkart v0.1.0

## Türkçe tercih edenler için:

***Those who prefer English can scroll down the page.***

## Açıklama

`skorkart`, BIST'te işlem gören hisselerin Halk Yatırım portalında yayımlanan finansal skor kart tablolarını Python ile kolayca çekmenizi sağlayan bir kütüphanedir. Kullanıcı dostu fonksiyonu ile bir veya birden fazla hisse, başlangıç ve bitiş dönemi seçimiyle verileri çekebilir; Türkçe veya İngilizce mesajlarla işlemlerinizi takip edebilirsiniz. Sonuçlar, her sekme ve hisse için ayrı ayrı pandas.DataFrame'ler içeren bir sözlük olarak döner ve isteğe bağlı olarak Excel'e kaydedilebilir.

## Özellikler

* Bir veya birden fazla hisse kodu için aynı anda veri çekimi
* Başlangıç ve bitiş dönemi aralığı seçimi (örn. 2019/12 - 2025/03)
* Finansallar, karlılık ve çarpanlar (Financials, Profitability, Multiples) sekmelerini seçerek veri çekme imkanı
* Mesajlar ve hata bildirimleri Türkçe/İngilizce destekli
* Sonuçlar, her sekme ve hisse için ayrı ayrı `pandas.DataFrame`'ler içeren bir sözlük olarak döner
* Çekilen verileri opsiyonel olarak Excel dosyasına kaydedebilirsiniz
* `merge_to_single_excel` parametresi ile esnek kayıt:
  * `True`: Her tablo için (ör. Financials) tek bir Excel dosyası, her hisse için ayrı sheet
  * `False`: Her tablo-hisse kombinasyonu için ayrı Excel dosyası
* Selenium ile güncel veriye, tarayıcı üzerinden ulaşım

## Kurulum

Kütüphaneyi yüklemek için şu adımları izleyin:

1. Python'ı yükleyin: https://www.python.org/downloads/
2. Terminal veya komut istemcisinde aşağıdaki komutu çalıştırın:

```bash
pip install skorkart
```

Belirli bir versiyonu yüklemek için:

```bash
pip install skorkart==0.1.0
```

Yüklü versiyonu kontrol etmek için:

```bash
pip show skorkart
```

## Fonksiyonlar

### `scorecard_data`

BIST hisse kodu ve dönem aralığı vererek Halk Yatırım portalından skor kart verisi çeker.

Parametreler:

* `stock_codes` (`list[str]` veya `str`): Tek bir hisse kodu veya birden fazla hisse kodu listesi (örn. "THYAO", ["THYAO", "GARAN"])
* `start_period` (`str`): Başlangıç dönemi (örn. '2019/12')
* `end_period` (`str`): Bitiş dönemi (örn. '2025/03')
* `lang` (`str`, varsayılan `"tr"`): Mesaj dili ("tr" veya "en")
* `save_to_excel` (`bool`, varsayılan `False`): Sonuçları Excel'e kaydetmek için True yapın
* `merge_to_single_excel` (`bool`, varsayılan `True`):
  * `True`: Her tablo için tüm hisseler aynı Excel dosyasında, her hisse için ayrı sheet olarak kaydedilir.
  * `False`: Her tablo-hisse kombinasyonu için ayrı bir Excel dosyası kaydedilir (örn. `financials_THYAO_201912_202503.xlsx`).
* `wait_seconds` (`float`, varsayılan `3`): Web işlemleri arası bekleme süresi
* `financials` (`bool`, varsayılan `True`): Finansallar sekmesini çekmek için
* `profitability` (`bool`, varsayılan `True`): Karlılık sekmesini çekmek için
* `multiples` (`bool`, varsayılan `True`): Çarpanlar sekmesini çekmek için

Dönüş:

* `{tab_name: {hisse_kodu: pandas.DataFrame, ...}}`: Her sekme için hisse kodunu anahtar olarak kullanarak doğrudan DataFrame'e erişebileceğiniz bir sözlük döner.

## Örnek Kullanım

```python
from skorkart import scorecard_data

# Tüm hisseler tek Excel dosyasında, her biri ayrı sheet olarak:
results = scorecard_data(
    stock_codes=["THYAO", "GARAN"],
    start_period="2019/12",
    end_period="2025/03",
    lang="tr",
    save_to_excel=True,
    merge_to_single_excel=True
)
# Excel'de: financials_201912_202503.xlsx içinde 'THYAO' ve 'GARAN' sheet'leri oluşur.

# Kodda DataFrame'lere doğrudan hisse adıyla erişebilirsiniz:
thy_financials = results["Financials"]["THYAO"]
garan_financials = results["Financials"]["GARAN"]

# Tüm finansalları dolaşmak için:
for hisse_adi, df in results["Financials"].items():
    print(f"{hisse_adi} finansalları:", df.head())
```

Ayrı ayrı dosya olarak kaydedilirse:

```python
results = scorecard_data(
    stock_codes=["THYAO", "GARAN"],
    start_period="2019/12",
    end_period="2025/03",
    lang="tr",
    save_to_excel=True,
    merge_to_single_excel=False
)
# Her hisse için: financials_THYAO_201912_202503.xlsx, financials_GARAN_201912_202503.xlsx gibi dosyalar oluşur.

# Kodda yine doğrudan:
thy_financials = results["Financials"]["THYAO"]
garan_financials = results["Financials"]["GARAN"]
```

## Notlar

* Kütüphane, Halk Yatırım'ın web sitesindeki verilere bağımlıdır. Portalda yapılan değişikliklerde, veri çekimi etkilenebilir. Lütfen [Halk Yatırım](https://analizim.halkyatirim.com.tr/) adresinden veri durumu ve güncelliğini kontrol edin.
* Selenium ve ChromeDriver kullanılır. Google Chrome bilgisayarınızda yüklü ve güncel olmalıdır.
* Geri bildirim ve katkılarınız için: [GitHub Repo](https://github.com/urazakgul/skorkart)
* Sorunlar veya öneriler için "Issue" bölümüne yeni başlık açabilirsiniz: [GitHub Issues](https://github.com/urazakgul/skorkart/issues)

## Sürüm Notları

### v0.1.0 - 26/07/2025

* İlk sürüm yayında.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır.

## For those who prefer English:

## Description

`skorkart` is a Python package to easily fetch financial scorecard tables for BIST stocks from the Halk Yatırım portal. With its user-friendly function, you can fetch data for one or multiple stocks over a selected period range, receive messages in Turkish or English, and get results as a dictionary containing separate pandas.DataFrames for each tab and stock code, optionally saving them to Excel.

## Features

* Fetch data for one or multiple stock codes simultaneously
* Choose start and end periods (e.g., 2019/12 - 2025/03)
* Select and fetch Financials, Profitability, and Multiples tabs
* All messages and error notifications support both Turkish and English
* Returns results as a dictionary with separate `pandas.DataFrame` for each tab and stock code
* Optionally save the fetched data to Excel files
* Flexible save option with the `merge_to_single_excel` parameter:
  * `True`: For each table, all stocks are saved in a single Excel file, with each stock as a separate sheet
  * `False`: For each table-stock combination, a separate Excel file is created (e.g. `financials_THYAO_201912_202503.xlsx`)
* Uses Selenium for browser automation to access up-to-date data

## Installation

To install the package:

1. Install Python: https://www.python.org/downloads/
2. Run the following command in your terminal or command prompt:

```bash
pip install skorkart
```

To install a specific version:

```bash
pip install skorkart==0.1.0
```

To check the installed version:

```bash
pip show skorkart
```

## Functions

### `scorecard_data`

Fetches scorecard data from Halk Yatırım portal for given BIST stock codes and period range.

Parameters:

* `stock_codes` (`list[str]` or `str`): Single stock code or a list of codes (e.g., "THYAO", ["THYAO", "GARAN"])
* `start_period` (`str`): Starting period (e.g., '2019/12')
* `end_period` (`str`): Ending period (e.g., '2025/03')
* `lang` (`str`, default `"tr"`): Language for messages ("tr" or "en")
* `save_to_excel` (`bool`, default `False`): Save the results to Excel if True
* `merge_to_single_excel` (`bool`, default `True`):
  * `True`: For each table, all stocks are saved in a single Excel file with a separate sheet per stock
  * `False`: For each table-stock combination, a separate Excel file is created (e.g. `financials_THYAO_201912_202503.xlsx`)
* `wait_seconds` (`float`, default `3`): Wait time between web actions (in seconds)
* `financials` (`bool`, default `True`): Fetch the Financials tab
* `profitability` (`bool`, default `True`): Fetch the Profitability tab
* `multiples` (`bool`, default `True`): Fetch the Multiples tab

Returns:

* `{tab_name: {stock_code: pandas.DataFrame, ...}}`: For each tab, returns a dictionary whose keys are stock codes and values are the corresponding DataFrames.

## Example Usage

```python
from skorkart import scorecard_data

# All stocks in one Excel file, each as a separate sheet:
results = scorecard_data(
    stock_codes=["THYAO", "GARAN"],
    start_period="2019/12",
    end_period="2025/03",
    lang="en",
    save_to_excel=True,
    merge_to_single_excel=True
)
# Excel output: financials_201912_202503.xlsx with 'THYAO' and 'GARAN' sheets.

# Directly access DataFrames by stock name:
thy_financials = results["Financials"]["THYAO"]
garan_financials = results["Financials"]["GARAN"]

# To iterate over all stocks' financials:
for stock_code, df in results["Financials"].items():
    print(f"Financials for {stock_code}:", df.head())
```

When saving as separate files:

```python
results = scorecard_data(
    stock_codes=["THYAO", "GARAN"],
    start_period="2019/12",
    end_period="2025/03",
    lang="en",
    save_to_excel=True,
    merge_to_single_excel=False
)
# Output: financials_THYAO_201912_202503.xlsx, financials_GARAN_201912_202503.xlsx

# Access DataFrames by stock code:
thy_financials = results["Financials"]["THYAO"]
garan_financials = results["Financials"]["GARAN"]
```

## Notes

* The library depends on data from the [Halk Yatırım](https://analizim.halkyatirim.com.tr/) portal. In case of changes or maintenance on the website, data fetching may be affected. Please check the portal for up-to-date data.
* Uses Selenium and ChromeDriver. Google Chrome must be installed and up-to-date on your system.
* Contributions and feedback are welcome: [GitHub Repo](https://github.com/urazakgul/skorkart)
* For issues or suggestions, please open a new topic in the "Issues" section: [GitHub Issues](https://github.com/urazakgul/skorkart/issues)

## Release Notes

### v0.1.0 - 26/07/2025

* First release published.

## License

This project is licensed under the MIT License.