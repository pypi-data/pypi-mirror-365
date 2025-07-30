# Клиент для взаимодействия со СМЭВ3 посредством Адаптера
## Подключение
settings:

    INSTALLED_APPS = [
        'smev_agent_client',
    ]


apps:

    from django.apps import AppConfig as AppConfigBase

    class AppConfig(AppConfigBase):
    
        name = __package__
    
        def __setup_agent_client(self):
            import smev_agent_client
    
            smev_agent_client.set_config(
                smev_agent_client.configuration.Config(
                    agent_url='http://localhost:8090',
                    system_mnemonics='MNSV03',
                    timeout=1,
                    request_retries=1,
                )
            )
    
        def ready(self):
            super().ready()
            self.__setup_agent_client()

## Эмуляция
Заменить используемый интерфейс на эмулирующий запросы:

    smev_agent_client.set_config(
        ...,
        smev_agent_client.configuration.Config(
            interface=(
                'smev_agent_client.contrib.my_edu.interfaces.rest'
                '.OpenAPIInterfaceEmulation'
            )
        )
    )

## Запуск тестов
    $ tox

## API

### Передача сообщения

    from smev_agent_client.adapters import adapter
    from smev_agent_client.interfaces import OpenAPIRequest

    class Request(OpenAPIRequest):

        def get_url(self):
            return 'http://localhost:8090/MNSV03/myedu/api/edu-upload/v1/multipart/csv'
    
        def get_method(self):
            return 'post'
    
        def get_files(self) -> List[str]:
            return [
                Path('files/myedu_schools.csv').as_posix()
            ]

    result = adapter.send(Request())
