# Desenvolvendo um Crawler API com Scrapy e Klein

## Escopo

Hoje vamos desenvolver uma API para buscar frases por tags no site http://quotes.toscrape.com/ . Nossa API deve receber uma tag como parâmetro, fazer o scraping da página e nos retornar um `json` contendo uma lista com as frases e autores pertencentes aquela tag.

### Exemplo

```


```

## Pré-Requisitos

- Python 3
- Pipenv

## Desenvolvendo o Crawler

Para desenvolver o nosso crawler nós vamos utilizar o Scrapy e o site fictício http://books.toscrape.com/ pertencente ao [Web Scraping Sandbox](http://toscrape.com/) do Scrapinghub.

### O que é o Scrapy?

Scrapy (pronounced skray-pee)[1] is a free and open source web crawling framework, written in Python. Originally designed for web scraping, it can also be used to extract data using APIs or as a general purpose web crawler.[2] It is currently maintained by Scrapinghub Ltd., a web scraping development and services company.

### Por que usar o Scrapy?

- Scrapy is an open source and free to use framework.
- It is easier to build and scale large crawling projects.
- It has a built-in mechanism called Selectors, for extracting the data from websites.
- It handles the requests asynchronously and it is fast.

### Mãos a obra

#### Configurando o projeto

1. Clone o repositório

`$ git clone https://github.com/betinacosta/scrapy-klein-tutorial.git`

2. Dento da pasta rode o seguinte comando:

`make setup`

Isso irá criar, ativar e instalar tanto o Scrapy quanto o Klein em um virtualenv para podermos utilziar. Caso tudo corra bem, você deve ver algo parecido com isso no seu terminal:

![imagem mostrando o nome do ambiente virtual entre parenteses antes do nome do repositório significando que ele foi ativado ](img/virtualenv.png)

Para testar que o Scrapy foi instalado corretamente, rode o comando abaixo para exibir a versão do framework:

`$ scrapy version`

#### Criando um projeto

1. O scrapy possui um comando para iniciar um projeto com tudo que precisamos, para isso basta rodar:

`$ scrapy startproject tutorial`

Esse comando gerou os seguintes arquivos:

- **scrapy.cfg**: deploy configuration file
- **items.py**: project items definition file
- **middlewares.py** :project middlewares file
- **pipelines.py**: project pipelines file
- **settings.py**: project settings file
- **spiders/**: a directory where you'll later put your spiders

Iremos nos aprofundar mais nesses arquivos conforme a necessidade surgir durante o tutorial.

#### Criando nosso primeiro spider

Spiders are classes that you define and that Scrapy uses to scrape information from a website. 

Vamos criar um arquivo chamado `quotes_spider.py` dentro da pasta `tutorial/tutorial/spiders` com o seguinte conteúdo:

```python
import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.log(">>>>>>>>>>>> " + response.url + " <<<<<<<<<<<<<<")
```

Ok, o que está acontecendo nesse arquivo? O método `start_requests` define (como o nome sugere) por onde o nosso spider vai começar suas atividades no site ou sites definidos na variável `urls` e qual método aplicar nesses sites, definidos na `callback`. 

O que estamos fazendo no método parse no momento é simplesmente logar a url do site visitado pelo nosso spider, mas futuramente iramos colher informações da página.

Para rodar a nossa spider vamos no entra no projeto e executar o spider:

`$ cd tutorial`
`$ scrapy crawl quotes`

A nossa mensagem super original junto com a url do site deve ter sido logada no nível de `DEBUG`

#### Entendo a página

Antes de começarmos a colher informações com o nosso spider, precisamos entender melhor a estrutura da página da qual queremos colher informações e nesses momentos precisaremos de um pouco de entendimento de dois dos quatro cavaleiros do apocalipse: HTML e CSS. A forma como iremos colher as informações que necessitamos do site será através de selectors. Vamos dar uma inspecionada no site e ver onde está localizada.

Vamos começar tentando localizar o texto `Quotes to Scrape`. Quando você inspecionar a página verá que ele se encontra dentro do `a` dentro do `h1` que se encontra dentro de uma div com a classe `col-md-8`. Como mostra a imagem abaixo:

![imagem mostrando a página de citações fictícia e o título Quotes to Scrape. Ao lado, o inspect do chrome aberto mostrando a div, classe, a e h1 mencionados no texto acima ](img/inspect.png)

Para testar se conseguimos selecionar esse texto através da classe e da tag, vamos utilizar uma ferramenta muito util do scrapy: o scrapy shell:

`$ scrapy shell http://books.toscrape.com/`

Esse comando irá baixar a página e nos fornecer um objeto `response` que nos permitirá fazer algumas operações. Para verificar se conseguimos selecionar o texto que desejamos, vamos executar:

`$ response.css("div.col-md-8>h1>a::text").extract_first()`

Funcionou \o/ 

![imagem com uma menina comemorando muito feliz com a família até que ela pega uma travessa da mesa e quebra para demonstrar sua felicidade](https://media.giphy.com/media/XGSqXkATD3Akw/giphy.gif)

Ok, mas que porra é essa? 

`response.css()` é o que utilizamos para selecionar elementos da página com base no css. Ele deve receber o caminho para o elemento desejado.

`div.page-header>h1>a::text` diz que queremos o texto do `a` que está dentro do `h1` que se encontra dentro da `div` que possui a classe `col-md-8`

`extract_first()` response.css nos retornará um `selector` e para extrair as informações que precisamos utilizamos o método `extract`. Porém ele nos retornará uma lista. Nesse caso específico como temos apenas um item como conteúdo, podemos usar uma variação desse método, o `extract_first` para pegarmos a informação desejada. 

#### Pegando as frases por tag

Beleza! Agora que já temos uma noção de como selecionar elementos da página, vamos tentar selecionar as frases de uma determinada tag.

Observando o site e as páginas das tags, vamos que a construção da url dessa página se mantém constante, por esse motivo vamos usar isso ao nosso favor.

`http://quotes.toscrape.com/tag/nome_da_tag`

Obs.: Há alguns problemas com essa abordagem, como por exemplo ser baseada no fato de que as urls sempre seguirão esse padrão, mas esse não é o objetivo do tutorial.

Nesse primeiro momento, vamos assumir uma tag fixa. Posteriormente, receberemos a tag como parâmetro na nossa API.

```py
import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self):
        self.tag = "inspirational"

    def start_requests(self):
        base_url = "http://quotes.toscrape.com/tag/"
        urls = [
            base_url + self.tag,
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.log(">>>>>>>>>>>> " + response.url + " <<<<<<<<<<<<<<")

```

O que fizemos foi adicionar uma tag fixa no `__init__` e utilizamos ela para montar a url no `start_requests`.

Agora, vamos analisar a página e ver como podemos pegar o texto e o author das citações.

![imagem da página mostrando várias citações uma abaixo da outra contendo citação, a pessoa autora e demais tags](img/quotes-list.png)

Podemos fazer isso selecionando a div que contem as citações e iterando sobre os seus seletores:

```python
import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self):
        self.tag = "inspirational"

    def start_requests(self):
        base_url = "http://quotes.toscrape.com/tag/"
        urls = [
            base_url + self.tag,
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        quotes_selectors = response.css("div.quote")

        for selector in quotes_selectors:

            quote = selector.css("span.text::text").extract_first()
            author = ?
```

Uma pausa para descobrir como obter a informação do autor. Fique a vontade para usar o scrapy shell e pedir ajuda para a minha pessoa :)

Beleza, se tudo der certo (deu sim, fé no pai), nós já temos todas as informações que precisamos. Agora vamos retornar essas informações. Para isso, vamos abrir o arquivo `tutorial/tutorial/items.py` e criar um Item. 

To define common output data format Scrapy provides the Item class. Item objects are simple containers used to collect the scraped data. They provide a dictionary-like API with a convenient syntax for declaring their available fields.

```python
import scrapy


class Quote(scrapy.Item):
    text = scrapy.Field()
    author = scrapy.Field()
```

E agora vamos importar no `quotes_spider.py` e utilizar no lugar das variáveis.

```python
import scrapy

from tutorial.items import Quote

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self):
        self.tag = "inspirational"

    def start_requests(self):
        base_url = "http://quotes.toscrape.com/tag/"
        urls = [
            base_url + self.tag,
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        quotes_selectors = response.css("div.quote")

        for selector in quotes_selectors:

            quote["text"] = selector.css("span.text::text").extract_first()
            quote["author"] = seu_codigo_bonitao
```

Beleza e como retornamos isso? A Scrapy spider typically generates many dictionaries containing the data extracted from the page. To do that, we use the yield Python keyword in the callback.

```python
import scrapy

from tutorial.items import Quote

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self):
        self.tag = "inspirational"

    def start_requests(self):
        base_url = "http://quotes.toscrape.com/tag/"
        urls = [
            base_url + self.tag,
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        quotes_selectors = response.css("div.quote")

        for selector in quotes_selectors:

            quote["text"] = selector.css("span.text::text").extract_first()
            quote["author"] = seu_codigo_bonitao

            yield quote
```

Pronto! Agora se rodarmos o nosso spider com `scrapy crawl quotes` vamos ver que as informações foram coletadas com sucesso.

![imagem mostrando o terminal com as informações sobre as citações](img/quotes-terminal.png)

Para finalizar o nosso crawler com chave de ouro, temos um outro detalhe importante para verificar: paginação. É necessário "repetir" esse procedimento para as próximos páginas de citações caso elas existam. Para isso, vamos adicionar uma lógica de paginação depois do nosso `for` e adicionar a variável `start_urls`no nosso `__init__`. Essa variável é necessária para que o método `response.urljoin` utilizado na paginação consiga se achar corretamente.

```python
import scrapy

from tutorial.items import Quote

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self):
        self.tag = "inspirational"
        self.start_urls = ["http://quotes.toscrape.com/"]

    def start_requests(self):
        base_url = "http://quotes.toscrape.com/tag/"
        urls = [
            base_url + self.tag,
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        quotes_selectors = response.css("div.quote")

        for selector in quotes_selectors:

            quote["text"] = selector.css("span.text::text").extract_first()
            quote["author"] = seu_codigo_bonitao

            yield quote

        next_page_url = response.css("li.next>a::attr(href)").extract_first()

        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)
```

Pronto! Com isso finalizamos nosso crawler e podemos partir para a API!

## Desenvolvendo a API

Agora que já temos o nosso spider pronto! Podemos seguir para o desenvolvimento da API com o Klein!

### Por que o Klein?

Mas Betina, com tantos frameworks mais conhecidos e estabelecidos, porque raios usar o Klein e não o Flask, o Bottle ou até mesmo o Django (você quer overkill, @?)?

Bom, lembra que lá em cima eu disse que o fato de o scrapy lidar com os requests de maneira assíncrona seria importante para esse tutorial? Então, por esse motivo ele não costuma conversar muito bem com esses frameworks que estão acostumados a fazer os requests de maneira síncrona. 

Klein is a micro-framework for developing production-ready web services with Python, built off Werkzeug and Twisted. O Twisted framework baseado em eventos que ajuda a lidar com assincronia no python.


### Montando o app.py

A sintaxe do Klein é bem parecida com a do Flask. para montar o esqueleto básico da nossa API basta criar um arquivo `app.py` na raiz do projeto. (fora do escopo do scrapy)

```py
from klein import Klein
app = Klein()

@app.route("/")
def index(request):
    return "Bom dia flor do dia"

app.run("localhost", 8080)
```

Vamos rodar esse pedaço para ver se funciona antes de seguir em frente:

`$ python app.py`

Agora vamos criar o endpoint para enviar uma tag parar ser pesquisada:

```py
from klein import Klein
app = Klein()

@app.route("/")
def index(request):
    return "Bom dia flor do dia"

@app.route('/search')
def get_quotes(request):
    content = json.loads(request.content.read())
    tag = content.get("tag")

app.run("localhost", 8080)
```

## Juntando tudo

### Spider Runner

Agora vamos criar um runner para o nosso spider. Isso ira possibilitar a execução programática do nosso spider. Para isso vamos criar o arquivo `spider_runner.py` no mesmo nível do app.py

```py
class SpiderRunner(CrawlerRunner):
    def crawl(self, spider, *args, **kwargs):
        self.items = []

        crawler = self.create_crawler(spider)
        crawler.signals.connect(self._collect_item, signals.item_scraped)

        deferred = self._crawl(crawler, *args, **kwargs)
        deferred.addCallback(self._return_items)

        return deferred

    def _collect_item(self, item, response, spider):
        self.items.append(item)

    def _return_items(self, result):
        return self.items
```

O método crawl será responsável por executar o nosso spider.

### De volta ao Spider

Antes de prosseguirmos com a API, precisamos preparar o nosso spider para receber um parâmetro. Vamos enviar a tag na construção da classe `QuotesSpider`.

```py
import scrapy

from tutorial.items import Quote

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, tag):
        self.tag = tag
        self.start_urls = ["http://quotes.toscrape.com/"]
```

### De volta a API

Agora vamos adicionar a chamada para o spider_runner no nosso endpoint e passar o parametro que o nosso Spider espera....

```py
@app.route('/search')
def get_quotes(request):
    content = json.loads(request.content.read())
    tag = content.get("tag")
   
    runner = SpiderRunner()

    deferred = runner.crawl(QuotesSpider, tag=tag)
    deferred.addCallback(return_spider_output)

    return deferred
```

...e criar a callback que passamos parra o `deferred`. Essa callback é necessária para fazer o encoding correto do json.

```py
def return_spider_output(output):
    _encoder = ScrapyJSONEncoder(ensure_ascii=False)
    return _encoder.encode(output)
```

Para finalizar vamos executar nosso projeto em uma aba no terminal:

`$ python app.py`

E rodar um curl passando uma tag como parâmetro!

`$ curl -X POST http://localhost:8080/search -H 'Content-Type: application/json' -H 'Postman-Token: 8990960a-fda0-4902-9594-12e9b56d88f2' -H 'cache-control: no-cache' -d '{"tag":"poetry"}'`

Pronto! Você tem uma API Spider rodando!

## Próximos passos

Há diversas melhorias que podem ser feitas, vou listar algumas delas como formas de expandir o projeto e dar continuidade ao aprendizado:

Viu algo que pode melhorar nesse tutorial? Não exite em abrir um PR! Aproveita que ainda dá tempo de garantir a Hacktobertfest!

## Contato

- **site**: https://betinacosta.dev/
- **twitter**: https://twitter.com/ngasonicunicorn
- **email**: bmcosta13@gmail.com

## Referências









