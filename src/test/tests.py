import pytest
import datetime
from src.main.main import MediaFile, WasmProcessor, User, Subscription

#---------------------------------------------------------------------------------------------------
# Тести для методу MediaFile.upload()

def test_upload_invalid_file_size_zero():
    """Техніка: BVA (Граничне значення). Негативний тест."""
    # Arrange
    file = MediaFile(file_name="test.mp4", file_size=0, format="mp4")

    # Act & Assert
    with pytest.raises(ValueError, match="Неприпустимий розмір"):
        file.upload()

def test_upload_valid_minimum_file_size():
    """Техніка: BVA (Граничне значення). Позитивний тест."""
    # Arrange
    file = MediaFile(file_name="tiny.mp4", file_size=1, format="mp4")

    # Act & Assert
    file.upload()
    assert True 

def test_upload_network_error_simulation():
    """Техніка: EP (Клас еквівалентності). Негативний тест."""
    # Arrange
    chunk_size = 1024 * 1024 * 5
    file = MediaFile(file_name="video_network_error.mp4", file_size=chunk_size + 100, format="mp4")

    # Act & Assert
    with pytest.raises(ConnectionError, match="Збій мережі"):
        file.upload()

def test_upload_normal_valid_file():
    """Техніка: EP (Клас еквівалентності). Позитивний тест."""
    # Arrange
    file = MediaFile(file_name="normal_video.mp4", file_size=2048, format="mp4")

    # Act & Assert
    file.upload()
    assert True

#---------------------------------------------------------------------------------------------------
# Тести для методу WasmProcessor.process()

def test_process_invalid_format():
    """Техніка: EP (Клас еквівалентності). Негативний тест."""
    # Arrange
    file = MediaFile(file_name="audio.mp3", file_size=1024, format="mp3")
    processor = WasmProcessor(target_format="mp4", target_bitrate=1000)

    # Act & Assert
    with pytest.raises(ValueError, match="не підтримується"):
        processor.process(file, is_user_premium=False)

def test_process_free_user_max_bitrate():
    """Техніка: BVA (Граничне значення). Позитивний тест."""
    # Arrange
    file = MediaFile(file_name="video.mp4", file_size=1024, format="mp4")
    processor = WasmProcessor(target_format="webm", target_bitrate=3000)

    # Act
    result = processor.process(file, is_user_premium=False)

    # Assert
    assert result == b"blob_data_result_after_processing"

def test_process_free_user_exceed_bitrate():
    """Техніка: BVA (Граничне значення). Негативний тест."""
    # Arrange
    file = MediaFile(file_name="video.mp4", file_size=1024, format="mp4")
    processor = WasmProcessor(target_format="webm", target_bitrate=3001)

    # Act & Assert
    with pytest.raises(PermissionError, match="доступний лише за Premium"):
        processor.process(file, is_user_premium=False)

def test_process_premium_user_high_bitrate():
    """Техніка: EP (Клас еквівалентності). Позитивний тест."""
    # Arrange
    file = MediaFile(file_name="hq_video.mov", file_size=1024, format="mov")
    processor = WasmProcessor(target_format="mp4", target_bitrate=8000)

    # Act
    result = processor.process(file, is_user_premium=True)

    # Assert
    assert result == b"blob_data_result_after_processing"

def test_process_corrupt_file():
    """Техніка: EP (Клас еквівалентності). Негативний тест."""
    # Arrange
    file = MediaFile(file_name="is_corrupted_data.mp4", file_size=2048, format="mp4")
    processor = WasmProcessor(target_format="mp4", target_bitrate=2000)

    # Act & Assert
    with pytest.raises(RuntimeError, match="Виявлено биті пікселі"):
        processor.process(file, is_user_premium=True)

#---------------------------------------------------------------------------------------------------
# Тести для методу User.batch_process_files()

def test_batch_process_not_logged_in():
    """Техніка: EP (Клас еквівалентності). Негативний тест."""
    # Arrange
    sub = Subscription(1, "ACTIVE", datetime.date(2025, 1, 1))
    user = User(user_id=1, email="test@mail.com", is_premium=False, subscription=sub)
    user.is_logged_in = False 
    file = MediaFile("vid.mp4", 1024, "mp4")
    processor = WasmProcessor("webm", 1500)

    # Act
    user.batch_process_files([file], processor)

    # Assert
    assert len(user.history) == 0

def test_batch_process_empty_list():
    """Техніка: BVA (Граничне значення - пустий масив). Позитивний тест."""
    # Arrange
    sub = Subscription(1, "ACTIVE", datetime.date(2025, 1, 1))
    user = User(user_id=1, email="test@mail.com", is_premium=True, subscription=sub)
    user.login()
    processor = WasmProcessor("webm", 1500)

    # Act
    user.batch_process_files([], processor)

    # Assert
    assert len(user.history) == 0

def test_batch_process_mixed_files():
    """Техніка: EP (Клас еквівалентності). Позитивний тест (оркестрація)."""
    # Arrange
    sub = Subscription(1, "ACTIVE", datetime.date(2025, 1, 1))
    user = User(user_id=1, email="test@mail.com", is_premium=True, subscription=sub)
    user.login()
    
    valid_file = MediaFile("good.mp4", 1024, "mp4")
    invalid_file = MediaFile("bad.mp3", 1024, "mp3") 
    processor = WasmProcessor("webm", 1500)

    # Act
    user.batch_process_files([valid_file, invalid_file], processor)

    # Assert
    assert len(user.history) == 2
    assert user.history[0].operation_type == "PROCESS_SUCCESS"
    assert user.history[1].operation_type == "PROCESS_FAILED"