# Generated by Django 3.0 on 2020-01-31 18:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=35)),
            ],
        ),
        migrations.CreateModel(
            name='Cidade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=19)),
                ('sigla', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sigla', models.CharField(default='', max_length=2)),
                ('nome', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Situacao_de_pagamento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('descricao', models.CharField(max_length=100)),
                ('descricao_detalhada', models.CharField(blank=True, default='', max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Status_avaliacoes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Tipo_Inscricao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=25)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=5)),
                ('status', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Titulacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('curso_formacao', models.CharField(max_length=100)),
                ('instituicao', models.CharField(blank=True, max_length=100, null=True)),
                ('celular', models.CharField(max_length=30)),
                ('cep', models.CharField(max_length=30)),
                ('endereco', models.TextField(max_length=300)),
                ('hash_confirm_register', models.CharField(blank=True, default='', max_length=128, null=True)),
                ('hash_confirm_senha', models.CharField(blank=True, default='', max_length=128, null=True)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.Area')),
                ('cidade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='user.Cidade')),
                ('estado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='user.Estado')),
                ('pais', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.Pais')),
                ('tipo_inscricao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.Tipo_Inscricao')),
                ('titulacao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.Titulacao')),
                ('user', models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Resumo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=400)),
                ('texto', models.TextField(max_length=5000)),
                ('palavras_chave', models.CharField(max_length=200)),
                ('usuario', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='user.Usuario')),
            ],
        ),
        migrations.CreateModel(
            name='Pagamento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_transacao', models.CharField(blank=True, default='', max_length=32, null=True)),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.Situacao_de_pagamento')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Usuario')),
            ],
        ),
        migrations.CreateModel(
            name='Instituicao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('ordem', models.IntegerField()),
                ('resumo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Resumo')),
            ],
        ),
        migrations.AddField(
            model_name='cidade',
            name='id_estado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.Estado'),
        ),
        migrations.CreateModel(
            name='Avaliacoes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observacao', models.TextField(blank=True, max_length=1000, null=True)),
                ('resumo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Resumo')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Status_avaliacoes')),
            ],
        ),
        migrations.CreateModel(
            name='Autores',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('email', models.EmailField(default='', max_length=100)),
                ('ordem', models.IntegerField()),
                ('instituicao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Instituicao')),
                ('resumo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Resumo')),
            ],
        ),
    ]
