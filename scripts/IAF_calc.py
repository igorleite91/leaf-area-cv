# importando apenas as funcoes necessarias que sao usadas no codigo
from os import path, listdir
from cv2 import imread, cvtColor, threshold, morphologyEx, getStructuringElement, COLOR_BGR2GRAY, THRESH_BINARY, MORPH_ELLIPSE, MORPH_OPEN
from skimage.measure import label, regionprops
from pandas import DataFrame

# inputs passiveis de modificacao
strPath = './Digitalizadas'  # pasta onde estãos as subpastas das fazendas
fazendas = listdir(strPath)

# funcao que faz o calculo de area foliar com base em limires de cor para descartar o fundo branco...
def calcula_area_foliar(imagePath:str,imgName:str):
    
    # Carregando a imagem e convertendo para escala de cinza
    imagem = imread(imagePath)
    imagem_cinza = cvtColor(imagem, COLOR_BGR2GRAY)
    
    # invertendo mascara onde as areas com valores 0 sera o fundo branco 
    imagem_cinza = 255 - imagem_cinza

    # Binarizando a imagem
    limiar = 150  # Defina um limiar adequado para a sua imagem
    imagem_binaria = threshold(imagem_cinza, limiar, 252, THRESH_BINARY)[1]

    # Removendo ruídos
    imagem_binaria = morphologyEx(imagem_binaria, MORPH_OPEN, getStructuringElement(MORPH_ELLIPSE, (30, 30)))

    # Rotulando as regiões de interesse
    rotulos = label(imagem_binaria, connectivity=2)

    # Calculando a área de cada região (folha)
    props = regionprops(rotulos)
    areas = [prop.area for prop in props]

    # Convertendo as áreas de pixels para cm²
    comprimento_régua_cm = 1  # Defina o comprimento da régua em cm
    comprimento_régua_pixels = 118  # Meça o comprimento da régua em pixels na imagem
    fator_conversão = (comprimento_régua_cm ** 2) / (comprimento_régua_pixels ** 2)
    areas_cm2 = [area * fator_conversão for area in areas]

    dictTeste = {imgName: areas_cm2}
    return dictTeste

# Processamento e aplicacao de calculo propriamente ditas 
for fazenda in fazendas:

    fazendaPathImagens = listdir(path.join(strPath,fazenda))
    areaImagens = []

    for imagem in fazendaPathImagens:

        imgPath = path.join(strPath,fazenda,imagem)
        areaImagens.append(calcula_area_foliar(imgPath,imagem))

    # Transformar os dados no formato desejado
    dados_formatados = []
    for dicionario in areaImagens:
        for chave, valores in dicionario.items():
            for valor in valores:
                if valor < 1:
                    pass
                else:
                    dados_formatados.append({"Imagem": chave, "IAF": float(valor)})

    # Criar o DataFrame a partir dos dados formatados e exportando como planilha do excel
    df = DataFrame(dados_formatados)
    df.to_excel(f'{fazenda}.xlsx', index=False)

    print(f'{fazenda} concluído!')
    