![DataSus Logo](https://github.com/lenon51/portfolio/blob/master/datasus/logo.png?raw=true)

# Projeto: Consultar todos os óbitos registrados no DataSus em 2018

## Resumo

A meta desse projeto é consultar todos os óbitos do ano de 2018 registrados no DataSus e criar visualizações a partir desses dados.

---

## Lógica

* Baixar os dados do DataSus de 2018 de todos os estados brasileiros e consolidar em um único CSV;
* Baixar o IDHM de 2010(última data desse registro) de todos os municípios brasileiros do site <a href='http://atlasbrasil.org.br/' target='_new'>atlasbrasil.org.br</a> e entender se existe uma correlação entre os óbitos e esse índice
* Baixar todos os CIDs (Código Internacional de Doenças) do site <a href='http://www.medicinanet.com.br' target='_new'>http://www.medicinanet.com.br</a>
* Criar visualizações para representar esses dados de forma intuitiva.

## Ferramentas
* ** ``python`` **
* ** ``tableau`` **
* ** ``datasus`` **
* ** ``atrasbrasil.com.br`` **
* ** ``medicinanet.com.br`` **


## Visualizações

* Quantidade de óbitos por cidade no ano de 2018
![DataSus](https://github.com/lenon51/portfolio/blob/master/datasus/g1.png?raw=true)


* Quantidade de óbitos por sexo e estado civil. É possível notar que homens casados morrem mais.
![DataSus](https://github.com/lenon51/portfolio/blob/master/datasus/g2.png?raw=true)


* Aqui um visão mais detalhada dos óbitos agrupado por CID e por sexo.
![DataSus](https://github.com/lenon51/portfolio/blob/master/datasus/g3g4.png?raw=true)



* Como é possível ver no gráfico anterior, a primeira causa morte em mulheres é infarto agudo do miocardio e a segunda causa morte é a diabetes no ano de 2018. O interessante desses dados é que a diabete pode levar a um infarto agudo do miocardio, entretanto no óbito constará que a mulher morreu de infarto e não da causa que levou a isso que no caso seria a diabete.
Segue um artigo interessante do Drauzio Varella que ilustra essa explicação: <a href='https://drauziovarella.uol.com.br/doencas-cronicas/diabetes/por-que-diabetes-aumenta-risco-de-doencas-cardiovasculares/' target='_new'>https://drauziovarella.uol.com.br/doencas-cronicas/diabetes/por-que-diabetes-aumenta-risco-de-doencas-cardiovasculares/</a>
Abaixo temos um gráfico agrupado por idade da primeira causa morte (esquerda) e a da segunda causa morte(direita) em mulheres
![DataSus](https://github.com/lenon51/portfolio/blob/master/datasus/g5g6.png?raw=true)



* Conforme gráfico anterior, a primeira causa morte em homens é infarto agudo do miocardio e a segunda causa morte é agressão por meio de disparo de outra arma de fogo ou de arma não especificada.
Abaixo temos um gráfico agrupado por idade da primeira causa morte (direita) e a da segunda causa morte(esquerda) em homens
![DataSus](https://github.com/lenon51/portfolio/blob/master/datasus/g7g8.png?raw=true)

* Segue link do Tableau para um gráfico mais interativo:
https://public.tableau.com/profile/lenon6986#!/vizhome/ProjetoTableau2/CidadeMaior


