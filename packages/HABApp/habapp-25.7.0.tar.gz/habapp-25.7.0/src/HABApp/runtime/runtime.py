import asyncio
from pathlib import Path

import eascheduler

import HABApp
import HABApp.config
import HABApp.core
import HABApp.mqtt.connection as mqtt_connection
import HABApp.parameters.parameter_files
import HABApp.rule.interfaces._http
import HABApp.rule_manager
import HABApp.util
from HABApp.core import Connections, shutdown
from HABApp.core.internals import setup_internals
from HABApp.core.internals.proxy import ConstProxyObj
from HABApp.core.wrapper import process_exception
from HABApp.openhab import connection as openhab_connection


class Runtime:

    def __init__(self) -> None:
        # Rule engine
        self.rule_manager: HABApp.rule_manager.RuleManager = None

    async def start(self, config_folder: Path) -> None:
        try:
            # shutdown setup
            shutdown.register(Connections.on_application_shutdown, msg='Shutting down connections')

            # setup exception handler for the scheduler
            eascheduler.set_exception_handler(lambda x: process_exception('HABApp.scheduler', x))

            file_watcher = HABApp.core.files.HABAppFileWatcher()
            shutdown.register(file_watcher.shutdown, msg='Shutdown file watcher')

            # replace proxy objects
            ir = HABApp.core.internals.ItemRegistry()
            eb = HABApp.core.internals.EventBus()
            file_manager = HABApp.core.files.FileManager(file_watcher)

            setup_internals(ir, eb, file_manager)
            assert isinstance(HABApp.core.Items, ConstProxyObj)
            HABApp.core.Items = ir
            assert isinstance(HABApp.core.EventBus, ConstProxyObj)
            HABApp.core.EventBus = eb

            file_manager.setup()

            # Load config
            HABApp.config.setup_habapp_configuration(config_folder)

            # generic HTTP
            await HABApp.rule.interfaces._http.create_client()

            # Connection setup
            openhab_connection.setup()
            mqtt_connection.setup()

            # File loader setup
            # Parameter Files
            await HABApp.parameters.parameter_files.setup_param_files()

            # Rule engine
            self.rule_manager = HABApp.rule_manager.RuleManager(self)
            await self.rule_manager.setup()

            Connections.application_startup_complete()

        except HABApp.config.InvalidConfigError:
            shutdown.request()
        except Exception as e:
            process_exception('Runtime.start', e)
            await asyncio.sleep(1)  # Sleep so we can do a graceful shutdown
            shutdown.request()
