from starlette_admin.contrib.sqla import Admin

from admin_panel.custom_views import *


def add_views(admin: Admin):
    admin.add_view(
        UserView(models.User,
                 icon='fa fa-user',
                 name='Пользователи',
                 label='Пользователи')
    )
    admin.add_view(
        LotteryView(models.Lottery,
                    icon='fa fa-list',
                    name='Лотарея',
                    label='Лотарея')
    )
    admin.add_view(
        PlayerView(models.Player,
                   identity='player',
                   icon='fa fa-users',
                   name='Игроки',
                   label='Игроки')
    )
    admin.add_view(
        WinnersView(models.Winners,
                    icon='fa fa-trophy',
                    name='Победители',
                    label='Победители')
    )
    admin.add_view(
        TransactionView(models.Transaction,
                        icon='fa-solid fa-money-bill-transfer',
                        name='Транзакции',
                        label='Транзакции')
    )
    admin.add_view(
        WithdrawRequestsView(models.WithdrawRequest,
                             icon='fa-solid fa-bell',
                             name='Запросы на вывод',
                             label='Запрос на вывод')
    )

    admin.add_view(
        SettingsView(models.Settings,
                     icon='fa fa-cog',
                     name='Настройки',
                     label='Настройка')
    )
    # admin.add_view(
    #     ModelView(models.StatisticRecords)
    # )
