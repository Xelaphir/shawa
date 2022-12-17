# Generated by Django 4.1.4 on 2022-12-17 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rarity', models.PositiveSmallIntegerField()),
                ('is_common', models.BooleanField(default=True)),
                ('cost', models.PositiveIntegerField()),
                ('min_weight', models.PositiveIntegerField()),
                ('max_weight', models.PositiveIntegerField()),
                ('weight_step', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=20)),
                ('name_in', models.CharField(max_length=20)),
                ('name_with', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ComponentOwnership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.component')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('components', models.ManyToManyField(through='core.ComponentOwnership', to='core.component')),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('rarity', models.PositiveSmallIntegerField(primary_key=True, serialize=False, unique=True)),
                ('percents', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DiscountOwnership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('discount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.discount')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('price', models.PositiveIntegerField()),
                ('is_private', models.BooleanField(default=True)),
                ('rating', models.PositiveIntegerField(default=0, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.customer')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeComposition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('net_weight', models.PositiveIntegerField()),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.component')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.recipe')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='composition',
            field=models.ManyToManyField(through='core.RecipeComposition', to='core.component'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.customer')),
                ('discount', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.discountownership')),
                ('recipes', models.ManyToManyField(to='core.recipe')),
            ],
        ),
        migrations.CreateModel(
            name='Lot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchaser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lot_purchaser', to='core.customer')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lot_seller', to='core.customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='discounts',
            field=models.ManyToManyField(through='core.DiscountOwnership', to='core.discount'),
        ),
        migrations.CreateModel(
            name='ComponentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20)),
                ('compability', models.ManyToManyField(to='core.componenttype')),
            ],
        ),
        migrations.AddField(
            model_name='componentownership',
            name='lot',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.lot'),
        ),
        migrations.AddField(
            model_name='componentownership',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.customer'),
        ),
        migrations.AddField(
            model_name='component',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.componenttype'),
        ),
    ]