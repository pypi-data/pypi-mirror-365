# FIDI Common Libraries

Bibliotecas compartilhadas entre os projetos da FIDI, desenvolvidas seguindo as melhores práticas de desenvolvimento Python.

## 📋 Visão Geral

Este projeto fornece um conjunto de bibliotecas reutilizáveis para automação, integração AWS, processamento de dados e utilitários comuns utilizados nos projetos da FIDI.

## 🚀 Funcionalidades Principais

- **Data**: Operações de banco de dados multi-SGBD (Oracle via oracledb, PostgreSQL, SQL Server)
- **Utils**: Sistema de logging estruturado para múltiplos SGBDs
- **Constants**: Constantes de status padronizadas e funções de conversão entre diferentes tipos de status
- **AWS**: Clientes padronizados para SQS, SNS, Lambda, S3 com configuração centralizada
- **Config**: Gerenciamento de parâmetros com cache e conversão automática de tipos
- **UI**: Componentes para automação de interfaces gráficas com Pywinauto, incluindo inspetor de elementos

## 📦 Instalação e Configuração

### Pré-requisitos
- Python 3.9+
- Poetry

### Instalação como Biblioteca
```bash
# Instalar via Poetry (recomendado)
poetry add git+https://github.com/your-org/fidi-common-libraries.git

# Ou via pip
pip install git+https://github.com/your-org/fidi-common-libraries.git
```

### Desenvolvimento Local
```bash
# Clone o repositório
git clone <repository-url>
cd fidi-common-libraries

# Instale as dependências
poetry install

# Ative o ambiente virtual
poetry shell
```

### Configuração de Desenvolvimento
```bash
# Instale os hooks de pre-commit
poetry run pre-commit install

# Execute os testes
poetry run pytest

# Verifique a cobertura de testes
poetry run pytest --cov=src --cov-report=html
```

## 🔧 Como Usar

### Módulo Data - Operações de Banco

```python
from fidi_common_libraries.data.db_data import DatabaseConfig, DatabaseQuery, ProcessosRpaInserter, ProcessosRpaUpdater
from datetime import datetime

# Configuração do banco
db_config = DatabaseConfig.from_env('RPA_')  # Usa variáveis RPA_DB_SERVER, etc.

# Inserir registro
inserter = ProcessosRpaInserter(db_config)
registro_id = inserter.insert(
    ambiente="PRD",
    produto="FIDI-ferias",
    versao="1.0.0",
    chapa="123456",
    statusexecucao="NOVO"
)

# Consulta segura
query = DatabaseQuery(db_config)
results = query.execute_query(
    "SELECT * FROM processosrpa WHERE statusexecucao = :status",
    {"status": "NOVO"}
)
```

### Módulo Config - Gerenciamento de Parâmetros

```python
from fidi_common_libraries.config.parametros import Parametros

# Inicializar o gerenciador de parâmetros
params = Parametros(ambiente="HML", produto="FIDI-ferias")

# Obter um parâmetro
url_api = params.get_parametro("URL_API", default="https://api.exemplo.com")

# Obter parâmetros por grupo
config_email = params.get_parametros_por_grupo("Email")

# Obter parâmetros por categorias específicas
config_ti = params.get_parametros_por_grupo("TI")  # Configurações técnicas
config_negocio = params.get_parametros_por_grupo("Negocio")  # Configurações de negócio
config_produto = params.get_parametros_por_grupo("Produto")  # Configurações do produto

# Atualizar um parâmetro
params.atualizar_parametro("TIMEOUT_API", 30)
```

### Módulo Utils - Logging e Status

```python
from fidi_common_libraries.utils.logger import registrar_log_banco
from fidi_common_libraries.constants.status import HubStatus, DBStatus, LogStatus, convert_status
import pyodbc

# Conexão com banco
conn = pyodbc.connect(connection_string)

# Registrar log (detecta automaticamente o tipo de banco)
registrar_log_banco(
    conn=conn,
    ambiente="PRD",
    produto="FIDI-ferias",
    versao="1.0.0",
    nivel="INFO",
    modulo="main",
    processo="processamento",
    acao="inicio",
    lote="LOTE001",
    mensagem="Processo iniciado",
    usuario="sistema",
    status_execucao=LogStatus.SUCESSO,
    hostname="server01",
    ip_origem="192.168.1.100"
)

# Usar constantes de status
status_db = DBStatus.NOVO
status_log = convert_status(status_db, 'db', 'log')
```

### Módulo AWS - Clientes Padronizados

```python
from fidi_common_libraries.aws.common_aws import AWSClientFactory, AWSConfig, create_message_with_metadata

# Configuração AWS
config = AWSConfig.from_env()  # Usa variáveis AWS_REGION, AWS_ACCESS_KEY_ID, etc.
factory = AWSClientFactory(config)

# Cliente SQS
sqs = factory.get_sqs_client()
message_id = sqs.send_message(
    queue_url="https://sqs.sa-east-1.amazonaws.com/123456789/my-queue",
    message={"data": "test"},
    message_attributes={"Type": {"StringValue": "ProcessData", "DataType": "String"}}
)
```

### Módulo UI - Automação de Interfaces Gráficas

```python
from fidi_common_libraries.ui import RMApplication, ElementFinder, UIInteractions, UIWaits, LocatorService

# Conectar ou iniciar aplicação RM
app = RMApplication()
app.connect_or_start()  # Conecta se existir ou inicia nova instância

# Aguardar aplicação ficar pronta
app.wait_for_application_ready(timeout=60)

# Obter janela principal ou TOTVS
main_window = app.get_main_window()
totvs_window = app.get_totvs_window()

# Navegação automática no sistema RM
from fidi_common_libraries.ui import RMNavigator, LocatorMode
navigator = RMNavigator(app.app, main_window)
success, button_text = navigator.navigate_to_element(
    {"title": "Encargos", "control_type": "TabItem"},
    {"title": "Contabilização", "control_type": "Pane"},
    {"title": "Geração dos Encargos", "control_type": "Button"}
)

# Login automatizado no sistema RM
from fidi_common_libraries.ui import RMStartLogin, LocatorService
locator_service = LocatorService("locators.yaml")
login_manager = RMStartLogin(locator_service)
success, rm_app = login_manager.start_and_login("HML", "FIDI-ferias")

# Seleção de ambiente no login
from fidi_common_libraries.ui import RMLoginEnvSelector
env_selector = RMLoginEnvSelector(login_window, locator_service)
success, alias = env_selector.select_environment("HML", "FIDI-ferias")

# Conexão dupla (win32 + uia) para análise
from fidi_common_libraries.ui import RMDualConnect
connector = RMDualConnect(output_dir="locators_output")
success, info = connector.connect_dual()

# Usar serviço de locators para elementos
locator_service = LocatorService("locators.yaml", mode=LocatorMode.PYWINAUTO)
login_criteria = locator_service.get_non_null_attributes("login_button")

# Encontrar elemento com critérios robustos
finder = ElementFinder()
button = finder.find_element(
    parent=main_window,
    primary_criteria=login_criteria,
    fallback_criteria=[{"auto_id": "btnSave"}]
)

# Interagir com elementos de forma segura
interactions = UIInteractions()
interactions.safe_click(button)

# Aguardar elementos ou condições
waits = UIWaits()
waits.wait_for_element_ready(button, timeout=10)

# Inspeção de elementos UI (ferramenta de desenvolvimento)
from fidi_common_libraries.ui.utils.inspector import UIElementInspectorAdvanced
inspector = UIElementInspectorAdvanced()
inspector.connect_to_application(window_title="TOTVS")
inspector.start_assisted_navigation()  # Navegação assistida com overlay visual

# Fechar aplicação quando terminar
app.close_application()  # Fecha apenas se foi iniciada por nós

# Configuração AWS
config = AWSConfig.from_env()  # Usa variáveis AWS_REGION, AWS_ACCESS_KEY_ID, etc.
factory = AWSClientFactory(config)

# Cliente SQS
sqs = factory.get_sqs_client()
message_id = sqs.send_message(
    queue_url="https://sqs.sa-east-1.amazonaws.com/123456789/my-queue",
    message={"data": "test"},
    message_attributes={"Type": {"StringValue": "ProcessData", "DataType": "String"}}
)

# Cliente SNS
sns = factory.get_sns_client()
sns.publish_message(
    topic_arn="arn:aws:sns:sa-east-1:123456789:my-topic",
    message=create_message_with_metadata({"event": "process_completed"}),
    subject="Processo Finalizado"
)

# Cliente Lambda
lambda_client = factory.get_lambda_client()
result = lambda_client.invoke_function(
    function_name="my-function",
    payload={"action": "process", "data": "test"}
)

# Cliente S3
s3 = factory.get_s3_client()
s3.upload_file("/path/to/file.txt", "my-bucket", "uploads/file.txt")
```

## 🏗️ Estrutura do Projeto

```
fidi-common-libraries/
├── src/
│   └── fidi_common_libraries/
│       ├── aws/          # Utilitários AWS
│       ├── config/       # Gerenciamento de configurações e parâmetros
│       ├── constants/    # Constantes e enums compartilhados
│       ├── data/         # Processamento de dados e acesso a banco
│       ├── ui/           # Automação de UI
│       │   ├── core/     # Componentes principais
│       │   ├── utils/    # Utilitários (inspector, screenshot)
│       │   └── locators/ # Serviços de locators
│       └── utils/        # Utilitários gerais e logging
├── tests/
│   ├── unit/            # Testes unitários
│   ├── integration/     # Testes de integração
│   └── e2e/            # Testes end-to-end
├── docs/               # Documentação
├── scripts/            # Scripts auxiliares
└── resources/          # Recursos estáticos
```

## 🧪 Testes

O projeto mantém uma cobertura de testes superior a 85%:

```bash
# Executar todos os testes
poetry run pytest

# Executar com cobertura
poetry run pytest --cov=src --cov-report=term-missing

# Executar apenas testes unitários
poetry run pytest tests/unit/
```

## 📊 Qualidade de Código

Ferramentas utilizadas:
- **Black**: Formatação automática
- **Flake8**: Linting
- **MyPy**: Verificação de tipos
- **Bandit**: Análise de segurança

```bash
# Formatação
poetry run black src/ tests/

# Linting
poetry run flake8 src/ tests/

# Verificação de tipos
poetry run mypy src/

# Análise de segurança
poetry run bandit -r src/
```

## 📚 Documentação

- [INSTALL.md](INSTALL.md) - Guia completo de instalação e uso
- [CHANGELOG.md](CHANGELOG.md) - Histórico de mudanças
- [STATUS_ATUAL.md](STATUS_ATUAL.md) - Estado atual do projeto
- [docs/UI_MODULE_GUIDE.md](docs/UI_MODULE_GUIDE.md) - Guia completo do módulo UI
- [docs/UI_INSPECTOR_GUIDE.md](docs/UI_INSPECTOR_GUIDE.md) - Guia do inspetor de elementos UI
- [docs/RM_NAVIGATOR_GUIDE.md](docs/RM_NAVIGATOR_GUIDE.md) - Guia do navegador RM
- [docs/RM_AUTOMATION_GUIDE.md](docs/RM_AUTOMATION_GUIDE.md) - Guia completo de automação RM
- [docs/LOCATOR_SERVICE_GUIDE.md](docs/LOCATOR_SERVICE_GUIDE.md) - Guia do serviço de locators

> **Nota**: A partir da versão 1.2.0, este projeto utiliza apenas a biblioteca `oracledb` para conexões Oracle, removendo a dependência do `cx_Oracle`.
>
> **Nota**: A versão 1.3.0 introduz o módulo `ui` para automação de interfaces gráficas com Pywinauto.
>
> **Nota**: A versão 1.3.1 adiciona funcionalidades avançadas de inicialização e gerenciamento da aplicação RM.
>
> **Nota**: A versão 1.3.2 introduz o LocatorService para gerenciamento de locators via arquivos YAML.
>
> **Nota**: A versão 1.3.3 aprimora o LocatorService com validação robusta e tratamento de valores vazios.
>
> **Nota**: A versão 1.3.4 adiciona modos de retorno parametrizáveis (STD e PYWINAUTO) ao LocatorService.
>
> **Nota**: A versão 1.3.5 expande o LocatorService com suporte a dimensões e cálculo de centro dos elementos.
>
> **Nota**: A versão 1.3.6 introduz o RMNavigator para navegação automática no sistema TOTVS RM.
>
> **Nota**: A versão 1.3.7 adiciona classes especializadas para RM: RMStartLogin (login automatizado), RMLoginEnvSelector (seleção de ambiente) e RMDualConnect (conexão dupla para análise).

## 🤝 Contribuição

1. Siga as diretrizes estabelecidas em `.amazonq/rules/`
2. Mantenha a cobertura de testes acima de 85%
3. Execute os pre-commit hooks antes de fazer commit
4. Atualize a documentação conforme necessário

## 📄 Licença

Este projeto está licenciado sob os termos definidos no arquivo [LICENSE](LICENSE).