# genobio20
<p align="center"> 
    <img src="static/static/img/Logo_site_05.png" width="250">
</p>
Sistema para gerenciar as inscrições dos usuários para o evento Genomics and Bioinformatics 20 Year.

## Inicializar banco de dados
    $ python3 manage.py makemigrations
    $ python3 manage.py migrate

## Popular banco de dados
Para popular o banco com as informações default, como: nomes dos países, cidades, estados, titulações e tipos de inscrições,  nós solicitamos ao `sqlite` que leia os dados do arquivo *db_default.sql* e importe para o *db.sqlite3*, que é o nosso banco de dados.
    $ sqlite3 db.sqlite3 < db_default.sql

## Inicalizar servidor de desenvolvimento
    $ python3 manage.py runserver