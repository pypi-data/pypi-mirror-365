import os
import asyncio
import logging
from aiohttp import ClientSession
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Wg_web_client.exceptions import WGAutomationError
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class WireGuardWebClient:
    def __init__(self, ip: str, download_dir: str, chromedriver_path: str = None):
        self.ip = ip
        self.download_dir = os.path.abspath(download_dir)
        self.chromedriver_path = chromedriver_path
        os.makedirs(self.download_dir, exist_ok=True)

    async def _setup(self):
        try:
            from .driver_factory import create_driver
            loop = asyncio.get_running_loop()
            self.driver = await loop.run_in_executor(None, create_driver, self.download_dir, self.chromedriver_path)
            self.wait = WebDriverWait(self.driver, 3)
        except Exception as e:
            logger.error(f"Error in _setup: {str(e)}")
            raise

    async def create_key(self, key_name: str) -> str:
        existing_conf_path = os.path.join(self.download_dir, f"{key_name}.conf")
        if os.path.exists(existing_conf_path):
            logger.info(f"⚠️ Ключ '{key_name}' уже существует, пропуск создания.")
            return existing_conf_path

        await self._setup()
        try:
            logger.info(f"Создание ключа: {key_name}")
            self.driver.get(f"http://{self.ip}")

            # Нажимаем кнопку "New"
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'New')]]"))).click()
            await asyncio.sleep(1)

            # Вводим имя ключа
            name_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Name']")))
            name_input.send_keys(key_name)
            await asyncio.sleep(1)

            # Нажимаем "Create"
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Create')]"))).click()
            await asyncio.sleep(3)  # Даём время интерфейсу создать ключ

            # Получаем список блоков клиентов
            client_blocks = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'relative overflow-hidden')]"))
            )

            target_block = None
            for block in reversed(client_blocks):
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    target_block = block
                    break
                except NoSuchElementException:
                    continue

            if not target_block:
                logger.error(f"❌ Не найден блок с ключом: {key_name}")
                raise WGAutomationError(f"Не найден блок с именем ключа '{key_name}'")

            await asyncio.sleep(2)  # Ждём появления ссылки на скачивание

            download_link = target_block.find_element(
                By.XPATH, ".//a[contains(@href, '/api/wireguard/client/') and contains(@href, '/configuration')]"
            )
            download_url = download_link.get_attribute("href")
            full_download_url = f"http://{self.ip}{download_url.lstrip('.')}" if not download_url.startswith(
                "http") else download_url

            self.driver.get(full_download_url)
            await asyncio.sleep(2)  # Ждём начала скачивания

            result = await self._get_latest_downloaded_conf(key_name)
            logger.info(f"✅ Ключ '{key_name}' успешно создан. Файл: {result}")
            return result
        except Exception as e:
            logger.error(f"Ошибка при создании ключа '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Ошибка закрытия драйвера: {str(e)}")

    async def _get_latest_downloaded_conf(self, key_name: str) -> str:
        try:
            target_path = os.path.join(self.download_dir, f"{key_name}.conf")
            for _ in range(30):
                candidates = [f for f in os.listdir(self.download_dir) if f.endswith(".conf") or f.endswith(".tmp")]
                if candidates:
                    candidates.sort(key=lambda x: os.path.getmtime(os.path.join(self.download_dir, x)), reverse=True)
                    source_path = os.path.join(self.download_dir, candidates[0])
                    if candidates[0].endswith(".tmp"):
                        logger.warning(f"Файл скачался как .tmp: {candidates[0]}")
                    os.rename(source_path, target_path)
                    return target_path
                await asyncio.sleep(1)
            logger.error("Файл конфигурации не найден после 30 попыток")
            raise WGAutomationError("Файл конфигурации не найден после скачивания")
        except Exception as e:
            logger.error(f"Ошибка в _get_latest_downloaded_conf: {str(e)}")
            raise

    async def delete_key(self, key_name: str) -> None:
        await self._setup()
        try:
            logger.info(f"Удаление ключа: {key_name}")
            self.driver.get(f"http://{self.ip}")

            client_blocks = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[contains(@class,'relative overflow-hidden')]")
                )
            )

            target_block = None
            for block in reversed(client_blocks):
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    target_block = block
                    break
                except NoSuchElementException:
                    continue

            if not target_block:
                logger.error(f"Ключ не найден для удаления: {key_name}")
                raise WGAutomationError(f"Не найден ключ для удаления: '{key_name}'")

            try:
                delete_button = target_block.find_element(By.XPATH, ".//button[@title='Delete Client']")
                delete_button.click()
                await asyncio.sleep(1)

                confirm_button = self.wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(text(),'Delete Client') and contains(@class,'bg-red-600')]"
                    ))
                )
                confirm_button.click()
            except (NoSuchElementException, ElementClickInterceptedException) as e:
                logger.warning(f"Не удалось нажать кнопку удаления: {e}")
                raise WGAutomationError("Удаление не удалось из-за проблем с элементами интерфейса.")

            file_path = os.path.join(self.download_dir, f"{key_name}.conf")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Файл конфигурации удалён: {file_path}")
                except OSError as e:
                    logger.error(f"Ошибка удаления файла {file_path}: {str(e)}")

            logger.info(f"Ключ успешно удалён: {key_name}")

        except (WGAutomationError, RuntimeError, OSError) as e:
            logger.error(f"Ошибка удаления ключа '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Ошибка закрытия драйвера: {str(e)}")

    async def get_key_status(self, key_name: str) -> bool:
        url = f"http://{self.ip}/api/wireguard/client"
        try:
            logger.info(f"Проверка статуса ключа: {key_name}")
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f"Ошибка запроса API {url}: Статус {resp.status}")
                        raise Exception(f"Ошибка запроса: {resp.status}")
                    data = await resp.json()

            for client in data:
                if client["name"] == key_name:
                    logger.info(f"Статус ключа '{key_name}': {'включен' if client['enabled'] else 'выключен'}")
                    return client["enabled"]

            logger.error(f"Клиент '{key_name}' не найден на сервере")
            raise Exception(f"Клиент '{key_name}' не найден на сервере.")
        except Exception as e:
            logger.error(f"Ошибка получения статуса для ключа '{key_name}': {str(e)}")
            raise

    async def enable_key(self, key_name: str) -> None:
        await self._setup()
        try:
            logger.info(f"Включение ключа: {key_name}")
            self.driver.get(f"http://{self.ip}")
            await asyncio.sleep(1)

            blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'border-b')]")
            for block in blocks:
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    try:
                        toggle = block.find_element(By.XPATH, ".//div[@title='Enable Client']")
                        toggle.click()
                        logger.info(f"✅ Ключ '{key_name}' включён")
                    except (NoSuchElementException, ElementClickInterceptedException):
                        logger.warning(f"⚠️ Ключ '{key_name}' уже включён или не кликабелен")
                    return
                except NoSuchElementException:
                    continue
            logger.error(f"Ключ '{key_name}' не найден для включения")
        except (OSError, RuntimeError) as e:
            logger.error(f"Ошибка включения ключа '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Ошибка закрытия драйвера: {str(e)}")

    async def disable_key(self, key_name: str) -> None:
        await self._setup()
        try:
            logger.info(f"Отключение ключа: {key_name}")
            self.driver.get(f"http://{self.ip}")
            await asyncio.sleep(1)

            blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'border-b')]")
            for block in blocks:
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    try:
                        toggle = block.find_element(By.XPATH, ".//div[@title='Disable Client']")
                        toggle.click()
                        logger.info(f"⛔ Ключ '{key_name}' отключён")
                    except (NoSuchElementException, ElementClickInterceptedException):
                        logger.warning(f"⚠️ Ключ '{key_name}' уже отключён или не кликабелен")
                    return
                except NoSuchElementException:
                    continue
            logger.error(f"Ключ '{key_name}' не найден для отключения")
        except (OSError, RuntimeError) as e:
            logger.error(f"Ошибка отключения ключа '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Ошибка закрытия драйвера: {str(e)}")
