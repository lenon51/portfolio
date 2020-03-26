![Instagram Logo](https://github.com/lenon51/portfolio/blob/master/instagram/logo_instagram.jpg?raw=true)

# Projeto: Instagram

## Resumo

A meta desse projeto foi criar uma conta no Instagram e interagir com usuários. Como base para o desenvolvimento do projeto utilizei o artigo que mencionou o projeto de Chris Buetti (https://www.codigofonte.com.br/artigos/ele-usou-python-aprendizado-de-maquina-e-instagram-para-comer-de-graca-em-nova-york).

---

## Lógica

* Consultar e salvar fotos
* Curtir e comentar
* Consultar e salvar seguidores do Instagram das cervejarias
* Seguir e desseguir
* Postar
* Assistir stories

## Ferramentas
* ** ``python`` **
* ** ``selenium`` **
* ** ``machine learning`` **
* ** ``instagram`` **
* ** ``opencv`` **
* ** ``mysql`` **


## Visualizações

* A ideia partiu desse artigo do código fonte<br>
![Ideia](https://github.com/lenon51/portfolio/blob/master/instagram/01_ideia.png?raw=true)

* Consultar e salvar fotos<br>
Após salvar as fotos, acesso cada imagem para coletar os dados como: curtidas, descrição, usuário que postou, usuários marcados na imagem, data de postagem e se é imagem ou vídeo. Como ponto de partida utilizei hashtags relacionadas a cerveja para salvar as fotos para postar e comentar.
![Imagem](https://github.com/lenon51/portfolio/blob/master/instagram/02_Consultar_imagem.gif?raw=true)

* Curtir e comentar as fotos<br>
![Curtir](https://github.com/lenon51/portfolio/blob/master/instagram/04_Comentar_imagem.gif?raw=true)

* Consultar e salvar seguidores do Instagram das cervejarias<br>
Foram escolhidas 5 cervejarias artesanais de Santos/SP para salvar os usuários: Everbrew, Demonho, Cais, Infected e Bicudo<br>
![Seguidores](https://github.com/lenon51/portfolio/blob/master/instagram/05_Consultar_seguidores.gif?raw=true)

* Seguir e desseguir<br>
Antes de seguir e desseguir os usuários, é acessado o perfil dos usuários e os seguintes dados são salvos: quantidade de publicações, quantidade de seguidores, quantidade de contas seguindo, através do nome do usuário avalio se é homem/mulher, se o perfil é público ou privado e a conta origem da cervejaria.<br>
![Seguir](https://github.com/lenon51/portfolio/blob/master/instagram/03_Seguir_deseguir.gif?raw=true)

*Postar
Antes de postar a imagem é aplicado um modelo preditivo para verificar quais fotos tem o maior potêncial de retorno de curtidas.<br>

Foram cadastradas algumas frases que teoricamente sempre encaixam em qualquer postagem como por exemplo:<br>
![Frase](https://github.com/lenon51/portfolio/blob/master/instagram/01_frase.png?raw=true)

Caso na imagem o número de pessoas seja mais do 50% da imagem, é escolhida outra imagem.<br>
![Opencv](https://github.com/lenon51/portfolio/blob/master/instagram/01_opencv.png)

A escolha das hashtags das imagens é feita através de um modelo preditivo que retorna as 5 hashtags mais significativas e é montado um template.<br>
![Template](https://github.com/lenon51/portfolio/blob/master/instagram/01_template.png)

E enfim posto a imagem<br>
![Postagem](https://github.com/lenon51/portfolio/blob/master/instagram/06_Postagem.gif?raw=true)