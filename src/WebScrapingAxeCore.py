from selenium import webdriver
from axe_selenium_python import Axe
import json
import os

# Configurações para o Driver do Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("incognito")

driver = webdriver.Chrome(options=chrome_options)

# Ler as URLs do arquivo
url_file_path = "urlList/url_list_alexa.txt"
with open(url_file_path, "r") as file:
    websites = file.read().splitlines()

for i, website in enumerate(websites):
    try:
        driver.get(website)

        # Aplicando os testes do Axe-core
        axe = Axe(driver)
        axe.inject()
        results = axe.run()

        page_results = {}

        # Recuperar as informações importantes dos resultados gerados pelo Axe-core
        for violation in results['violations']:
            description = violation['description']
            impact = violation['impact']
            tags = violation['tags']
            nodes = len(violation['nodes'])
            page_results[description] = {
                'impact': impact,
                'tags': tags,
                'num_nodes_violated': nodes
            }

        # Extrair o nome do site da URL para gerar o arquivo JSON com o nome do site
        site_name = website.split('.')[1]
        print(site_name)
        
        json_file_name = f"{site_name}.json"

        # Path para salvar os resultados em arquivos JSON
        results_dir = "jsonResults"
        
        os.makedirs(results_dir, exist=True)
        
        json_file_path = os.path.join(results_dir, json_file_name)

        # Salvar os resultados em um arquivo JSON correspondente ao site
        with open(json_file_path, "w") as f:
            json.dump(page_results, f, indent=4)

    except Exception as e:
        print(f"Error analyzing website: {website}")
        print(f"Exception message: {str(e)}")

    print(f"Progress: {i+1}/{len(websites)}")
