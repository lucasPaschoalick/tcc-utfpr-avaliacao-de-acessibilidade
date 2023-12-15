from selenium import webdriver
from axe_selenium_python import Axe
import json
import os
import time
import matplotlib.pyplot as plt
import numpy as np

# funçoes do projeto

# Função para extrair as informações necessárias dos resultados do Axe-core
def extract_info(results):
    violations_info = []
    for violation in results["violations"]:
        description = violation["description"]
        impact = violation["impact"]
        tags = violation["tags"]
        nodes = len(violation["nodes"])
        violation_info = {
            "description": description,
            "impact": impact,
            "tags": tags,
            "num_nodes_violated": nodes,
        }
        violations_info.append(violation_info)
    return violations_info

# Função para salvar screenshot da tela de cada site
def save_site_screenshot(driver, site):
    screenshot_name = f"{site}.png"    
    screenshot_path = os.path.join(screenshot_dir, screenshot_name)
    driver.save_screenshot(screenshot_path)

# Função para executar os testes
def axe_test(driver, site):
    axe = Axe(driver)
    axe.inject()
    results = axe.run()
    
    results_name = f"{site}.json"
    results_path = os.path.join(json_results_dir, results_name)
    
    with open(results_path, "w") as f:
        json.dump(results, f, indent=4)
    
    violations_info = extract_info(results)
    filtered_results_path = os.path.join(filtered_results_dir, results_name)
    with open(filtered_results_path, "w") as f:
        json.dump(violations_info, f, indent=4)
    
    return violations_info

# Função para salvar json com sites que deram erro no teste
def save_error_sites(error_list):
    error_sites_file = "errorSites.json"    
    error_sites_path = os.path.join(error_sites_dir, error_sites_file)
    
    with open(error_sites_path, "w") as f:
        json.dump(error_list, f, indent=4) 
        
# Função para salvar json com sites sem erro no teste
def save_sites_without_violations(sites_without_violations):
    with open('sites_sem_violacoes.json', 'w') as json_file:
        json.dump(sites_without_violations, json_file, indent=4, ensure_ascii=False)
        
# Função para criar e salvar gráficos
def create_bar_graph(data_dict, title, x_label, y_label, identifier=0, show_legend=False, rotation=90):
    plt.figure(figsize=(20, 15))

    if identifier == 0:
        sorted_dict = dict(sorted(data_dict.items(), key=lambda item: item[1], reverse=True))
        x_values = list(sorted_dict.keys())
        y_values = list(sorted_dict.values())
    elif identifier == 1:
        sorted_dict = dict(sorted(data_dict.items(), key=lambda item: item[1]["count"], reverse=True))
        x_values = list(sorted_dict.keys())
        y_values = [sorted_dict[description]["count"] for description in x_values]

    plt.bar(x_values, y_values)

    if show_legend:
        plt.legend()

    plt.xticks(rotation=rotation)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    
    # Aumentar o tamanho do texto no eixo x e quebrar linhas por palavra
#     x_values_formatted = []
#     for text in x_values:
#         words = text.split(' ')
#         lines = []
#         line_length = 0
#         line = []
#         for word in words:
#             if line_length + len(word) > 100:
#                 lines.append(' '.join(line))
#                 line = [word]
#                 line_length = len(word)
#             else:
#                 line.append(word)
#                 line_length += len(word)
#         lines.append(' '.join(line))
#         x_values_formatted.append('\n'.join(lines[:10]))
    
#     plt.xticks(range(len(x_values)), x_values_formatted, fontsize=15)
#     plt.gca().tick_params(axis='x', which='major', pad=20)

    plt.tight_layout()

    graph_image_name = title
    graphs_path = os.path.join('images/imageGraphs', graph_image_name + ".png")
    plt.savefig(graphs_path)

# Função para criar pastas do projeto
def make_dir(dir_name):    
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

# Função para contabilizar a ocorrência de cada violação por descrição
def count_occurrences_by_description(violations_info):
    violations_count = {}
    
    for site_violations in violations_info:
        for violation in site_violations:
            description = violation["description"]
            
            if description not in violations_count:
                violations_count[description] = 0
            
            violations_count[description] += 1
    
    return violations_count

# Função para calcular a media de ocorrências de cada violação
def average_violations_by_description(results_dir):
    total_violations_by_description = {}
    total_violations = 0

    json_files = [f for f in os.listdir(results_dir) if f.endswith(".json")]

    for json_file in json_files:
        with open(os.path.join(results_dir, json_file), "r") as f:
            results = json.load(f)

        for violation in results:
            description = violation["description"]
            num_violations_node = violation["num_nodes_violated"]

            if description not in total_violations_by_description:
                total_violations_by_description[description] = 0

            total_violations_by_description[description] += num_violations_node
            total_violations += num_violations_node

    average_violations = {}

    for description, total_violations_for_type in total_violations_by_description.items():
        percentage = (total_violations_for_type / total_violations) * 100
        average_violations[description] = percentage

    return average_violations

# Função para contar o número de websites que apresentam determinadas violações
def count_websites_by_violation(results_dir, total_violations_by_description):
    websites_by_violation = {}
    
    for description in total_violations_by_description.keys():        
        websites_by_violation[description] = {"sites": [], "count": 0}
    
    # Listar os arquivos JSON na pasta de resultados
    json_files = [f for f in os.listdir(results_dir) if f.endswith(".json")]

    for json_file in json_files:
        with open(os.path.join(results_dir, json_file), "r") as f:
            results = json.load(f)

        site_name = json_file.split(".json")[0]

        for violation in results:
            description = violation["description"]
            websites_by_violation[description]["sites"].append(site_name)
            websites_by_violation[description]["count"] += 1

    return websites_by_violation

# Função para salvar arquivos JSON
def save_to_json(data, output_file):
    with open(output_file, "w") as json_file:
        json.dump(data, json_file, indent=4)
        
start_time = time.time()

# Configurações para o Driver do Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1280x720")
chrome_options.add_argument("incognito")

driver = webdriver.Chrome(options=chrome_options)

driver.set_script_timeout(3)

# Criação de diretórios para armazenar os arquivos
all_results_dir = make_dir("results")
json_results_dir = make_dir("results/jsonResults")
filtered_results_dir = make_dir("results/filteredResults")
sites_with_no_error = make_dir("results/sitesWithNoError")
error_sites_dir = make_dir("results/sitesWithError")

images_dir = make_dir("images")
screenshot_dir = make_dir("images/screenshots")
graphs_dir = make_dir("images/imageGraphs")

# Declaração de Dicionários e listas
violations_count = {}
sites_violations_count = {}
error_sites = []
sites_sem_violacoes = []

# lista de sites
url_path = "urlList/url_list_alexa.txt"
with open(url_path, "r") as file:
    websites = file.read().splitlines()

# Iteração nos websites para executar os testes
for i, website in enumerate(websites):
    try:
        driver.get(website)        
        
        site = website.split('.')[1]
        
        save_site_screenshot(driver, site)
        violations_info = axe_test(driver, site)
    
        if violations_info is None or not violations_info:
            sites_sem_violacoes.append(site)

    except Exception as e:
        print(f"Erro ao analisar o website: {website}")
        print(e)
        error_sites.append(website)
        
    print(website)
    print(f"Progresso: {i+1}/{len(websites)}")

save_error_sites(error_sites)

save_sites_without_violations(sites_sem_violacoes)

occurrences_by_description = count_occurrences_by_description(violations_info)
save_to_json(occurrences_by_description, "violations_occurrences.json")

driver.quit()

end_time = time.time()
elapsed_time = end_time - start_time
        
print(f"Tempo de execução: {elapsed_time:.2f} segundos")

# Calcular Média de violações por Websites e Número de Websites para Cada Violação e salvar em JSON
results_dir = "results/filteredResults"

average_violations = average_violations_by_description(results_dir)
save_to_json(average_violations, "average_violations.json")

websites_by_violation = count_websites_by_violation(results_dir, average_violations)
save_to_json(websites_by_violation, "count_websites_by_violation.json")

with open('media_violacoes.json', 'r', encoding='utf-8') as file:
    media_violacoes = json.load(file)
    
with open('websites_por_violacao.json', 'r', encoding='utf-8') as file:
    websites_por_violacao = json.load(file)
    
# Criar gráficos
create_bar_graph(media_violacoes, "Média de ocorrência das violações", "Violações", "Porcentagem de Ocorrências", identifier=0)
create_bar_graph(websites_por_violacao, "Número de Websites para Cada Violação", "Descrição da Violação", "Número de Websites", identifier=1)

# create_bar_graph(media_violacoes, "Média de ocorrência das violações (10 mais frequentes)", "Violações", "Porcentagem de Ocorrências", identifier=0)
# create_bar_graph(websites_por_violacao, "Número de Websites para Cada Violação (10 mais frequentes)", "Descrição da Violação", "Número de Websites", identifier=1)