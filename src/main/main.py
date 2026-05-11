import datetime
from typing import List

# --- Клас Підписки ---
class Subscription:
    def __init__(self, sub_id: int, status: str, expiry_date: datetime.date):
        self.sub_id = sub_id
        self.status = status
        self.expiry_date = expiry_date
    def activate(self) -> None:
        if self.status == "ACTIVE":
            print(f"Підписка {self.sub_id} вже активна.")
            return
        self.status = "ACTIVE"
        self.expiry_date = datetime.date.today() + datetime.timedelta(days=30)
        print(f"Підписка {self.sub_id} успішно активована до {self.expiry_date}.")

# --- Клас Медіафайлу ---
class MediaFile:
    def __init__(self, file_name: str, file_size: int, format: str):
        self.file_name = file_name
        self.file_size = file_size  # Розмір у байтах
        self.format = format

    # НЕТРИВІАЛЬНИЙ МЕТОД 1: Цикл while, умовні конструкції та винятки
    def upload(self) -> None:
        if self.file_size <= 0:
            raise ValueError(f"Помилка: Неприпустимий розмір файлу {self.file_name}.")
        print(f"Початок завантаження файлу {self.file_name} ({self.file_size} байт)...")
        chunk_size = 1024 * 1024 * 5  # 5 MB шматки
        uploaded = 0
        while uploaded < self.file_size:
            uploaded += chunk_size
            if uploaded > self.file_size:
                uploaded = self.file_size
            percent = (uploaded / self.file_size) * 100
            print(f"Завантажено: {uploaded}/{self.file_size} байт ({percent:.1f}%)")
            
            # Штучна перевірка мережі (імітація помилки за певних умов)
            if "network_error" in self.file_name and uploaded >= chunk_size:
                raise ConnectionError("Збій мережі під час завантаження.")
                
        print("Завантаження успішно завершено.\n")

    def download(self) -> None:
        print(f"Завантаження файлу {self.file_name} на пристрій...\n")

# --- Клас Історії ---
class HistoryRecord:
    def __init__(self, record_id: int, timestamp: datetime.datetime, operation_type: str, media_file: MediaFile):
        self.record_id = record_id
        self.timestamp = timestamp
        self.operation_type = operation_type
        self.media_file = media_file  # Зв'язок 1 до 1 з MediaFile

    def save_locally(self) -> None:
        print(f"[LOG] Збереження в локальну БД: ID={self.record_id}, Операція={self.operation_type}, Файл={self.media_file.file_name}")

# --- Клас Процесора ---
class WasmProcessor:
    def __init__(self, target_format: str, target_bitrate: int):
        self.target_format = target_format
        self.target_bitrate = target_bitrate

    def set_parameters(self, format: str, bitrate: int) -> None:
        self.target_format = format
        self.target_bitrate = bitrate
        print(f"Параметри WasmProcessor оновлено: формат={format}, бітрейт={bitrate}kbps")

    # НЕТРИВІАЛЬНИЙ МЕТОД 2: Валідація з винятками, логіка Premium, цикл обробки
    def process(self, file: MediaFile, is_user_premium: bool) -> bytes:
        allowed_input_formats = ["mp4", "webm", "avi", "mov"]

        if file.format not in allowed_input_formats:
            raise ValueError(f"Формат {file.format} не підтримується для обробки.")

        # Бізнес-логіка: обмеження для безкоштовних акаунтів
        if not is_user_premium and self.target_bitrate > 3000:
            raise PermissionError("Бітрейт понад 3000 kbps доступний лише за Premium-підпискою.")

        print(f"Конвертація '{file.file_name}' з {file.format} у {self.target_format} з бітрейтом {self.target_bitrate}kbps...")

        # Імітація обробки шматками (цикл)
        steps = 4
        for i in range(1, steps + 1):
            if "corrupt" in file.file_name.lower() and i == 2:
                raise RuntimeError("Виявлено биті пікселі або пошкоджені дані у файлі.")
            print(f"...Обробка Wasm: {i * (100 // steps)}%")
            
        print("Обробку файлу завершено успішно.")
        # Повертаємо результат у вигляді байтів (імітація Blob)
        return b"blob_data_result_after_processing"

# --- Клас Користувача ---
class User:
    def __init__(self, user_id: int, email: str, is_premium: bool, subscription: Subscription):
        self.user_id = user_id
        self.email = email
        self.is_premium = is_premium
        self.subscription = subscription       # Зв'язок 1 до 1 з Subscription
        self.history: List[HistoryRecord] = [] # Зв'язок 1 до багатьох з HistoryRecord
        self.is_logged_in = False

    def login(self) -> bool:
        self.is_logged_in = True
        print(f"Користувач {self.email} увійшов у систему.\n")
        return True

    def logout(self) -> None:
        self.is_logged_in = False
        print(f"Користувач {self.email} вийшов із системи.\n")

    # НЕТРИВІАЛЬНИЙ МЕТОД 3: Пакетна обробка, обробка винятків (try-except) та керування колекціями
    def batch_process_files(self, files: List[MediaFile], processor: WasmProcessor) -> None:
        if not self.is_logged_in:
            print("Спершу потрібно увійти в систему.")
            return

        print(f"--- Початок пакетної обробки {len(files)} файлів для {self.email} ---")
        
        for file in files:
            try:
                # 1. Завантаження файлу (може викликати ConnectionError/ValueError)
                file.upload()
                
                # 2. Обробка процесором (може викликати ValueError/RuntimeError/PermissionError)
                result_blob = processor.process(file, self.is_premium)
                
                # 3. Успішне завершення - додаємо запис в історію
                record = HistoryRecord(
                    record_id=len(self.history) + 1,
                    timestamp=datetime.datetime.now(),
                    operation_type="PROCESS_SUCCESS",
                    media_file=file
                )
                self.history.append(record)
                record.save_locally()
                print("--------------------------------------------------")

            except (ConnectionError, ValueError, PermissionError, RuntimeError) as e:
                # Відловлюємо помилки, але продовжуємо обробляти наступні файли
                print(f"[ПОМИЛКА] Збій під час операції з '{file.file_name}': {e}")
                
                # Фіксуємо помилку в історії
                error_record = HistoryRecord(
                    record_id=len(self.history) + 1,
                    timestamp=datetime.datetime.now(),
                    operation_type="PROCESS_FAILED",
                    media_file=file
                )
                self.history.append(error_record)
                error_record.save_locally()
                print("--------------------------------------------------")