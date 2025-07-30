# Ganim 🎨

**Uma biblioteca Python intuitiva para treinar e usar Redes Adversariais Generativas (GANs) para geração de imagens.**

A Ganim foi projetada para simplificar o processo de criação com GANs. Ela abstrai a complexidade do código de baixo nível, permitindo que você inicie um treinamento completo ou gere arte digital com uma API simples e direta.

## ✨ Principais Recursos

- **API Simplificada:** Comandos intuitivos como `fit()`, `sample()` e `show()` para um fluxo de trabalho rápido e eficiente.
- **Altamente Configurável:** Use a função `setup()` para ajustar facilmente os principais parâmetros do seu modelo, como épocas de treino e taxa de aprendizado.
- **Visualização Integrada:** Monitore o progresso do seu treino com prévias automáticas e exiba suas imagens finais em janelas de alta resolução.
- **Análise de Performance:** Plote gráficos de perda do Gerador e do Discriminador com uma única linha de código usando `plot()`.
- **Gerenciamento de Modelos:** Salve seus modelos com `save()` e carregue-os a qualquer momento com `load()` para continuar de onde parou.

## ⚙️ Instalação

*Instruções de instalação para a biblioteca serão fornecidas aqui quando disponível.*

**Pré-requisitos:**
A Ganim depende das seguintes bibliotecas Python. Certifique-se de que elas estejam instaladas no seu ambiente:
- `torch` e `torchvision`
- `numpy`
- `matplotlib`
- `opencv-python`
- `tqdm`

Você pode instalá-las usando pip:
```bash
pip install torch torchvision numpy matplotlib opencv-python tqdm
```


## 🚀 Guia Rápido (Quick Start)

**Para começar, organize suas imagens de treinamento na seguinte estrutura de pastas:**

```bash
seu_projeto/
├── imgs/
│   └── dataset/  <-- Uma subpasta (qualquer nome)
│       ├── imagem1.jpg
│       └── imagem2.png
│
└── seu_script.py
```
*Com a Ganim, treinar um modelo e gerar imagens é muito simples:*

```python

import ganim

# --- 1. TREINAMENTO ---

# (Opcional) Configure os parâmetros do seu projeto
ganim.setup(
    epochs=500,               # Número de épocas de treinamento
    sampleInterval=50,        # Frequência para gerar prévias
    previewImageCount=25,     # Quantidade de imagens na prévia (grid 5x5)
    previewWindowSize=768     # Tamanho da janela de prévia em pixels
)

# Inicia o treinamento
"O 'fit' retorna o modelo Gerador treinado e um histórico de perdas"
generator, history = ganim.fit(data='./imgs')

 "Se o treino ocorreu bem, plote a performance e salve o modelo"
if generator and history:
    ganim.plot(history)
    ganim.save(generator, path='./meu_modelo_ganim.pth')


# --- 2. GERAÇÃO ---

" Carregue seu modelo treinado"
meu_gerador = ganim.load(path='./meu_modelo_ganim.pth')

"Gere 16 novas imagens"
novas_imagens = ganim.sample(model=meu_gerador, count=16)

 "Exiba as imagens em uma janela grande e personalizada"
ganim.show(
    novas_imagens,
    window_title="Arte Gerada por Ganim!",
    window_size=1024
)

```


## 📚 Referência da API

# Aqui estão as principais funções disponíveis no ganim:


`ganim.setup(**kwargs)`


**Configura os hiperparâmetros globais. Deve ser chamada antes de fit().**

`ganim.fit(data)`

**Inicia o loop de treinamento. Retorna o modelo Gerador treinado e um dicionário de historico.**

`ganim.sample(model, count=1)`

**Gera novas imagens a partir de um modelo treinado.**

`ganim.show(images_tensor, window_title="Ganim", window_size=None)`

**Exibe um tensor de imagens em uma janela.**

`ganim.plot(history)`

**Plota os gráficos de perda do treinamento.**

`ganim.save(model, path="ganim_model.pth")`

**Salva os pesos de um modelo em um arquivo.**

`ganim.load(path)`

**Carrega os pesos de um modelo salvo. Retorna um novo objeto Gerador.**



| Parâmetro           | Padrão | Descrição                                                                 |
| ------------------- | ------ | ------------------------------------------------------------------------- |
| `imageSize`         | 64     | Resolução da imagem (pixels). A arquitetura atual é otimizada para 64x64. |
| `channels`          | 3      | Canais de cor (3 para RGB, 1 para escala de cinza).                       |
| `latentDim`         | 100    | Dimensão do vetor de ruído (a "semente" da imagem).                       |
| `epochs`            | 5000   | Número total de épocas de treinamento.                                    |
| `batchSize`         | 64     | Quantidade de imagens processadas por lote.                               |
| `learningRate`      | 0.0002 | Taxa de aprendizado dos modelos.                                          |
| `sampleInterval`    | 100    | Frequência (em épocas) para gerar prévias do progresso.                   |
| `previewImageCount` | 16     | Quantidade de imagens exibidas por prévia.                                |
| `previewWindowSize` | 512    | Tamanho (em pixels) da janela de prévia.                                  |
