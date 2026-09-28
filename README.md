<div align="center">

<img src="docs/img/logo.png" width="110" alt="leaf-area-cv">

# leaf-area-cv

### Medição automática de **área foliar** a partir de folhas digitalizadas em scanner

*Um scanner de mesa, uma régua e ~2 segundos por imagem substituem horas de medidor de bancada.*

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![scikit-image](https://img.shields.io/badge/scikit--image-regionprops-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-image.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-notebooks-F37626?logo=jupyter&logoColor=white)](https://jupyter.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-2f6b42.svg)](LICENSE)
[![Made in Brazil](https://img.shields.io/badge/made%20in-Brazil%20%F0%9F%87%A7%F0%9F%87%B7-009B3A)](#)

**[Português](README.md)** · [English](README.en.md)

</div>

---

<div align="center">
<img src="docs/img/pipeline.png" width="100%" alt="Pipeline: scanner → máscara binária → folhas segmentadas com área em cm²">
<sub><i>Resultado real do repositório: 5 folhas de eucalipto digitalizadas, segmentadas e medidas automaticamente.</i></sub>
</div>

---

## O problema

Medir área foliar é uma das tarefas mais repetitivas da pesquisa agronômica e florestal. Os
caminhos usuais são caros ou lentos:

| Método | Custo | Tempo por folha | Destrutivo |
|---|---|---|---|
| Medidor óptico de bancada (LI-3100, CI-202…) | R$ 30–80 mil | ~5 s | sim |
| Papel milimetrado / pesagem de recortes | baixo | 2–5 min | sim |
| Modelos alométricos (comprimento × largura) | baixo | ~1 min | não |
| **Este repositório** | **scanner comum** | **~0,4 s** | sim |

Se você já tem um scanner de mesa, o custo marginal é zero.

## O que este código faz

1. Lê cada imagem digitalizada e converte para escala de cinza.
2. **Inverte** a máscara, de modo que o fundo branco do scanner vire zero.
3. **Binariza** por limiar fixo — separa o tecido foliar (escuro) do fundo (claro).
4. **Abertura morfológica** com elemento elíptico 30×30 px, removendo poeira, fiapos e
   os traços finos da régua.
5. **Rotula regiões conexas** e mede a área de cada uma em pixels.
6. **Converte px² → cm²** pelo fator de calibração da régua presente na imagem.
7. Descarta regiões < 1 cm² (ruído residual e as marcações da régua).
8. Exporta **uma planilha `.xlsx` por pasta/talhão**, uma linha por folha.

A versão `IAF_comp_larg` mede, além da área, o **comprimento** e a **largura** de cada folha,
pelos eixos maior e menor da elipse equivalente (`regionprops`).

## Começando em 3 minutos

```bash
git clone https://github.com/igorleite91/leaf-area-cv.git
cd leaf-area-cv
pip install -r requirements.txt

# roda no conjunto de exemplo já incluído no repositório
cd exemplos
python ../scripts/IAF_calc.py
```

Saída esperada — um arquivo `Fazenda_Exemplo_01.xlsx` com 10 linhas (5 folhas × 2 imagens):

| Imagem | IAF |
|---|---|
| A1_I.1.jpg | 49.4512 |
| A1_I.1.jpg | 45.0063 |
| A1_I.1.jpg | 15.8868 |
| A1_I.1.jpg | 44.3997 |
| A1_I.1.jpg | 43.3875 |
| A1_I.1_semRegua.jpg | 49.4503 |
| … | … |

*(áreas em cm², uma linha por folha detectada; valores conferidos com
scikit-image 0.26 / OpenCV 4.x)*

Note que as duas imagens de exemplo são a mesma cena, com e sem a régua no campo de visão:
a diferença nas áreas fica na quarta casa decimal — ou seja, **a régua não contamina a
medição**, porque a abertura morfológica e o corte de 1 cm² a eliminam.

## Estrutura esperada das pastas

O script percorre `./Digitalizadas`, trata **cada subpasta como um grupo** (talhão, fazenda,
tratamento, bloco…) e gera uma planilha por grupo:

```
Digitalizadas/
├── Fazenda_Exemplo_01/     →  Fazenda_Exemplo_01.xlsx
│   ├── A1_I.1.jpg
│   └── A1_I.1_semRegua.jpg
├── Tratamento_T2/          →  Tratamento_T2.xlsx
│   └── ...
└── Bloco_III/              →  Bloco_III.xlsx
```

## Calibração — leia antes de usar nos seus dados

> [!IMPORTANT]
> **O fator de conversão é específico do seu scanner.** Os valores abaixo valem para as
> imagens de exemplo (300 dpi). Se você não ajustar, todas as áreas sairão erradas por um
> fator constante.

```python
comprimento_régua_cm    = 1     # trecho de referência, em cm
comprimento_régua_pixels = 118  # o MESMO trecho, medido em pixels na sua imagem
```

Como medir: digitalize uma régua junto com as folhas, abra a imagem em qualquer visualizador
que mostre coordenadas de pixel (GIMP, ImageJ, Paint), e conte quantos pixels há entre duas
marcas de 1 cm.

Atalho pela resolução do scanner — `pixels_por_cm = dpi / 2,54`:

| Resolução | px por cm |
|---|---|
| 150 dpi | 59 |
| **300 dpi** | **118** ← usado nos exemplos |
| 600 dpi | 236 |

### Demais parâmetros ajustáveis

| Parâmetro | Padrão | Quando mexer |
|---|---|---|
| `limiar` | `150` (`100` na versão comp/larg) | Folhas claras/cloróticas exigem limiar menor; fundo acinzentado exige maior |
| `janela_suavizacao` | `(30, 30)` | Diminua para folhas pequenas (acículas, gramíneas); aumente se sobrar sujeira |
| corte `área < 1 cm²` | `1` | Ajuste se suas folhas forem menores que 1 cm² — senão elas serão descartadas junto com o ruído |

## Boas práticas de digitalização

- **Fundo branco e limpo.** A tampa branca do scanner já basta; papel amassado cria sombras
  que o limiar interpreta como tecido.
- **Folhas sem encostar umas nas outras.** Duas folhas em contato viram uma única região e
  somam áreas.
- **Régua na mesma imagem**, na mesma altura do vidro — assim a calibração acompanha
  qualquer variação de resolução.
- **300 dpi é suficiente** para folhas de árvores. Resoluções maiores só aumentam o tempo.
- **Evite folhas muito curvas.** A área projetada subestima a área real de folhas enroladas;
  prense antes se possível.

## O que há no repositório

```
leaf-area-cv/
├── scripts/
│   ├── IAF_calc.py              # área foliar, lote de pastas → .xlsx
│   └── IAF_comp_larg.py         # área + comprimento + largura → .xlsx
├── notebooks/
│   ├── 01_areaFoliar_imagem_unica.ipynb     # didático: uma imagem, passo a passo
│   ├── 02_areaFoliar_lote.ipynb             # processamento em lote
│   └── 03_area_comprimento_largura.ipynb    # + inspeção visual do limiar
├── exemplos/Digitalizadas/Fazenda_Exemplo_01/
│   ├── A1_I.1.jpg               # 5 folhas de eucalipto + régua, 300 dpi
│   └── A1_I.1_semRegua.jpg      # mesma cena sem a régua
└── docs/img/
```

Os três notebooks já apontam para o conjunto de exemplo — abra qualquer um deles a partir da
pasta `notebooks/` e execute tudo, sem configurar nada. As saídas gravadas no repositório
foram produzidas exatamente assim, sobre as imagens que acompanham o código.

> **Dica:** o notebook `03` traz uma célula de inspeção visual que plota a máscara aplicada
> sobre a imagem original. Use-a para calibrar o `limiar` antes de rodar o lote inteiro.

## Precisão e limitações

Vale a pena ser explícito sobre o que este método é e o que ele não é:

- **Mede área projetada**, não área de superfície. Para folhas planas os dois valores são
  próximos; para folhas com nervura saliente ou enroladas, há subestimação.
- **O nome da coluna não descreve a grandeza.** `IAF_calc.py` grava a coluna como `IAF` e
  `IAF_comp_larg.py` como `AFE`, mas em **ambos os casos o valor é a área foliar individual
  em cm²** — nem Índice de Área Foliar (LAI), nem Área Foliar Específica (SLA). Para obter o
  IAF/LAI, some as áreas da amostra e divida pela área de solo correspondente; para a AFE/SLA,
  divida a área pela massa seca da folha. Os nomes foram mantidos por compatibilidade com as
  planilhas já em uso — renomeie no seu fluxo se preferir clareza.
- **`Comprimento` e `Largura`** são os eixos maior e menor da *elipse de mesmo segundo
  momento* da região, calculados por `skimage.measure.regionprops`. São excelentes
  descritores morfométricos e correlacionam muito bem com medidas de paquímetro, mas não
  são idênticos a elas — especialmente em folhas assimétricas ou falcadas.
- **`regionprops` mudou de nomenclatura.** A partir do scikit-image 0.26,
  `major_axis_length` e `minor_axis_length` estão marcados como obsoletos e serão removidos
  na versão 2.0, em favor de `axis_major_length` e `axis_minor_length`. O
  `requirements.txt` limita a versão a `<2.0` por isso; quando migrar, é só trocar os dois
  nomes em `IAF_comp_larg.py`.
- **Limiar global fixo.** Funciona muito bem com fundo branco controlado de scanner. Para
  fotografias de campo, com iluminação irregular, um limiar adaptativo (Otsu local) ou
  segmentação por índice de cor daria resultados melhores.
- **Folhas em contato são contadas como uma só.** Separe-as no vidro.

## Aplicações

Área foliar e morfometria alimentam diretamente:

- **Fenotipagem vegetal** — triagem de genótipos, ensaios de melhoramento
- **Silvicultura** — eucalipto, pinus; acompanhamento de crescimento e resposta a adubação
- **Fitopatologia** — quantificação de severidade (área lesionada / área total)
- **Ecofisiologia** — área foliar específica (AFE/SLA), quando combinada com massa seca
- **Nutrição de plantas** — normalização de teores por unidade de área
- **Ensino** — um exemplo compacto e real de morfologia matemática e análise de regiões

## Instalação

```bash
pip install -r requirements.txt
```

Ou, individualmente:

```bash
pip install opencv-python scikit-image pandas openpyxl matplotlib numpy
```

## Como citar

Se este código for útil em trabalho acadêmico, a citação está no arquivo
[`CITATION.cff`](CITATION.cff) — o GitHub gera BibTeX/APA automaticamente pelo botão
**"Cite this repository"** na barra lateral.

## Contribuindo

Issues e pull requests são bem-vindos. Melhorias que fariam diferença real:

- [ ] Limiarização automática por Otsu, dispensando o ajuste manual
- [ ] Detecção automática da régua, dispensando a calibração manual
- [ ] Separação de folhas sobrepostas por *watershed*
- [ ] Interface gráfica ou linha de comando com argumentos
- [ ] Validação cruzada contra um medidor óptico comercial

## Licença

[MIT](LICENSE) — uso livre, inclusive comercial. Atribuição é apreciada.

---

<div align="center">
<sub>Desenvolvido por <a href="https://github.com/igorleite91">Igor Leite</a> · Se foi útil, deixe uma ⭐</sub>
</div>
