import os
import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QScrollArea, QLabel, QHBoxLayout, QFrame, QSizePolicy,
                            QPushButton, QLineEdit, QCheckBox, QComboBox, QStatusBar,
                            QSpinBox, QMessageBox)
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor
from PyQt5.QtCore import Qt, QSize


class ThumbnailWidget(QFrame):
    def __init__(self, folder_path, preview_path, tags=None, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.preview_path = preview_path
        self.folder_name = os.path.basename(folder_path)
        self.tags = tags or []
        self.setMinimumHeight(190)
        self.setMaximumHeight(190)
        self.setStyleSheet("""
            QFrame {
                background-color: #fff;
                margin: 5px 0;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        
        # Preview image
        self.image_label = QLabel()
        self.image_label.setFixedSize(170, 110)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #1e1e1e;
            border: 1px solid #444;
            border-radius: 3px;
        """)
        
        # Load preview image if exists
        if os.path.exists(preview_path):
            pixmap = QPixmap(preview_path)
            if not pixmap.isNull():
                # Scale image to fit while maintaining aspect ratio
                pixmap = pixmap.scaled(180, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(pixmap)
        
        # Create container for image and button
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(5)
        
        # Add image to container
        image_layout.addWidget(self.image_label)
        
        # Add "Открыть больше" button below image
        self.open_more_btn = QPushButton("Открыть больше")
        self.open_more_btn.setStyleSheet("""
            QPushButton {
                padding: 5px;
                color: #333;
                min-width: 100px;
                border: 1px solid #555;
                border-radius: 3px;
                background: #fff;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #4CAF50;
                color: #ffffff;
                border: 1px solid #4CAF50;
            }
            QPushButton:focus {
                border: 1px solid #4CAF50;
            }
        """)
        self.open_more_btn.clicked.connect(self.load_random_texture)
        image_layout.addWidget(self.open_more_btn)
        
        # Right side container for text
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)
        
        # Title row with folder name, input field, and checkbox
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 10, 0, 0)
        title_row.setSpacing(15)

        # Title row with folder name, input field, and checkbox
        title_row2 = QHBoxLayout()
        title_row2.setContentsMargins(0, 0, 0, 0)
        title_row2.setSpacing(15)
        
        # Initialize name label (will be updated after loading workshop data)
        self.name_label = QLabel(os.path.basename(folder_path))
        self.name_label.setStyleSheet("""
            color: #333;
            font-size: 16px;
            font-weight: bold;
            min-width: 278px;
            max-width: 278px;
        """)
        
        # Tag dropdown
        self.tag_dropdown = QComboBox()
        self.tag_dropdown.setStyleSheet("""
            QComboBox {
                padding: 3px 5px;
                color: #333;
                min-width: 200px;

                background: #fff;
            }
            QComboBox:focus {
                border: 1px solid #2E2E2EFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """)
        
        # Add tags to dropdown
        self.tag_dropdown.addItem("Выберите тег")  # Default empty option
        for tag in self.tags:
            self.tag_dropdown.addItem(tag)
        
        # Container for selected tags
        self.selected_tags_layout = QHBoxLayout()
        self.selected_tags_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_tags_layout.setSpacing(5)
        
        # Label for selected tags
        tags_label = QLabel("Теги:")
        tags_label.setStyleSheet("color: #666; font-size: 14px; font-weight:bold;")
        self.selected_tags_layout.addWidget(tags_label)
        
        # Store selected tags for this game
        self.current_tags = set()
        
        # Checkbox
        self.checkbox = QCheckBox("Отметить игру")
        self.checkbox.setFixedSize(50, 25)
        self.checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 0px;
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 45px;
                height: 20px;
                border: 2px solid #7E7E7E;
                border-radius: 4px;
                background: #3a3a3a;
            }
            QCheckBox::indicator:checked {
                background: #4CAF50;
                border-radius: 4px;
                border: 2px solid #85D487
            }
        """)
        self.checkbox.stateChanged.connect(self.toggle_game_id)

        self.button = QPushButton("Добавить тег")
        self.button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                color: #333;
                min-width: 100px;
                border: 1px solid #555;
                border-radius: 3px;
                background: #fff;
            }
            QPushButton:hover {
                background: #4CAF50;
                color: #ffffff;
                border: 1px solid #4CAF50;
            }
            QPushButton:focus {
                border: 1px solid #4CAF50;
            }
        """)


        
        self.button.clicked.connect(self.add_tag_to_game)

        self.trash_button = QPushButton("🗑️")
        self.trash_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                color: #333;
                min-width: 20px;
                border: 1px solid #555555;
                border-radius: 3px;
                background: #fff;
            }
            QPushButton:hover {
                background: #EEEEEE;
                color: #ffffff;
                border: 1px solid #808080;
            }
            QPushButton:focus {
                border: 1px solid #4CAF50;
            }
        """)


        
        self.button.clicked.connect(self.send_in_trash)
        
        # Add widgets to title row in the new order
        title_row.addWidget(self.name_label)
        title_row.addWidget(self.tag_dropdown)
        title_row.addWidget(self.button)
        title_row.addWidget(self.checkbox)


        title_row.addStretch()
        
        # Add rows to text layout
        text_layout.addLayout(title_row)
        
        # Add description field between title and tags
        desc_row = QHBoxLayout()
        desc_row.setContentsMargins(0, 0, 0, 0)
        desc_row.setSpacing(10)
        
        desc_label = QLabel("Описание:")
        desc_label.setStyleSheet("color: #666; font-size: 14px; min-width: 80px; font-weight:bold;")
        
        self.desc_input = QLineEdit()
        self.desc_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                color: #333;
                background: #fff;
                max-width: 612px;
            }
            QLineEdit:focus {
                border: 3px solid #4CAF50;
            }
        """)
        self.desc_input.setPlaceholderText("Введите описание игры...")
        # Save description on Enter
        self.desc_input.returnPressed.connect(self.save_description)
        
        desc_row.addWidget(desc_label)
        desc_row.addWidget(self.desc_input)
        desc_row.addStretch()

                # Add information row below tags
        info_row = QHBoxLayout()
        info_row.setContentsMargins(0, 5, 0, 0)
        info_row.setSpacing(10)
        
        info_label = QLabel("Информация:")
        info_label.setStyleSheet("color: #666; font-size: 14px; min-width: 80px; font-weight:bold;")
        
        # Load and display mod settings info
        self.mod_info_label = QLabel("")
        self.mod_info_label.setStyleSheet("color: #666; font-size: 12px; min-width: 500px;")
        self.mod_info_label.setWordWrap(True)
        self.mod_info_label.setOpenExternalLinks(True)  # Enable external links
        self.mod_info_label.setTextInteractionFlags(Qt.TextBrowserInteraction)  # Make text selectable and clickable
        
        info_row.addWidget(info_label)
        info_row.addWidget(self.mod_info_label)
        info_row.addStretch()
        
        
        
        text_layout.addLayout(desc_row)
        text_layout.addLayout(info_row)
        text_layout.addLayout(title_row2)
        
        # Add selected tags container to the second row
        title_row2.addLayout(self.selected_tags_layout)
        title_row2.addStretch()
        

        
        # Load existing tags if any
        self.load_existing_tags()
        
        # Load game info and workshop data
        self.game_info = self.load_game_info()
        self.workshop_data = self.load_workshop_data()
        
        # Load mod settings (after UI is fully created)
        self.load_mod_settings()
        
        # Store original preview path for restoration
        self.original_preview_path = preview_path
        
        # Set initial checkbox state based on general_info.json
        self.update_checkbox_state()
        
        # If workshop data is available, update the UI
        if self.workshop_data:
            # Update the name label with the workshop title if it exists, otherwise keep folder name
            if 'title' in self.workshop_data and self.workshop_data['title']:
                self.name_label.setText(self.workshop_data['title'])
            
            # The text input is used for tags, so we don't auto-populate it with the title
            
            # Display description if needed
            if 'description' in self.workshop_data:
                description = self.workshop_data['description']
                # You can use this description as needed
                print(f"Description for {self.folder_name}: {description}")
            
            # Display tags if needed
            if 'tags' in self.workshop_data and isinstance(self.workshop_data['tags'], list):
                tags = ", ".join(self.workshop_data['tags'])
                # You can use these tags as needed
                print(f"Tags for {self.folder_name}: {tags}")
        
        # Add the image container to the layout
        layout.addWidget(image_container)
        
        # Add text container with name
        text_layout.addStretch()
        
        layout.addWidget(text_container, stretch=1)
        layout.addStretch()
        
        # Make it clickable
        self.setCursor(Qt.PointingHandCursor)
        
        # Add mouse press event to toggle checkbox when clicking on background
        self.mousePressEvent = self.on_mouse_press
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    def load_random_texture(self):
        """Load random texture from Assets/Textures/ folder"""
        try:
            textures_folder = os.path.join(self.folder_path, "Assets", "Textures")
            
            if os.path.exists(textures_folder):
                # Get all JPG files from textures folder
                jpg_files = []
                for file in os.listdir(textures_folder):
                    if file.lower().endswith('.jpg'):
                        jpg_files.append(file)
                
                if jpg_files:
                    # Select random JPG file
                    import random
                    random_file = random.choice(jpg_files)
                    random_file_path = os.path.join(textures_folder, random_file)
                    
                    # Load and display random texture
                    pixmap = QPixmap(random_file_path)
                    if not pixmap.isNull():
                        # Scale image to fit while maintaining aspect ratio
                        pixmap = pixmap.scaled(180, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.image_label.setPixmap(pixmap)
                        
                        # Change button text to indicate we can go back
                        self.open_more_btn.setText("Вернуть превью")
                        self.open_more_btn.clicked.disconnect()
                        self.open_more_btn.clicked.connect(self.restore_preview)
                    else:
                        print(f"Error loading texture: {random_file_path}")
                else:
                    print(f"No JPG files found in {textures_folder}")
            else:
                print(f"Textures folder not found: {textures_folder}")
                
        except Exception as e:
            print(f"Error loading random texture: {e}")
    
    def restore_preview(self):
        """Restore original preview image"""
        try:
            if hasattr(self, 'original_preview_path') and os.path.exists(self.original_preview_path):
                pixmap = QPixmap(self.original_preview_path)
                if not pixmap.isNull():
                    # Scale image to fit while maintaining aspect ratio
                    pixmap = pixmap.scaled(180, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_label.setPixmap(pixmap)
                    
                    # Restore button functionality
                    self.open_more_btn.setText("Открыть больше")
                    self.open_more_btn.clicked.disconnect()
                    self.open_more_btn.clicked.connect(self.load_random_texture)
                    
        except Exception as e:
            print(f"Error restoring preview: {e}")
    
    def load_workshop_data(self):
        # Load workshop data from WorkshopItem.json
        workshop_file = os.path.join(os.path.dirname(self.preview_path), "WorkshopItem.json")
        if os.path.exists(workshop_file):
            try:
                with open(workshop_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading workshop data for {self.folder_name}: {e}")
        return {}
    
    def load_mod_settings(self):
        """Load mod settings from ModSettings.json"""
        mod_settings_file = os.path.join(self.folder_path, "Data", "ModSettings.json")
        
        if os.path.exists(mod_settings_file):
            try:
                with open(mod_settings_file, 'r', encoding='utf-8') as f:
                    mod_data = json.load(f)
                    
                    # Try different possible structures
                    info_parts = []
                    
                    # Check for NumberOfRounds in SimpleMinigameSettings
                    rounds = None
                    if "SimpleMinigameSettings" in mod_data and "NumberOfRounds" in mod_data["SimpleMinigameSettings"]:
                        rounds = mod_data["SimpleMinigameSettings"]["NumberOfRounds"]
                    
                    if rounds is not None:
                        info_parts.append(f"Число раундов: {rounds}")
                    
                    # Check for RoundDuration in SimpleMinigameSettings
                    duration = None
                    if "SimpleMinigameSettings" in mod_data and "RoundDuration" in mod_data["SimpleMinigameSettings"]:
                        duration = mod_data["SimpleMinigameSettings"]["RoundDuration"]
                    
                    if duration is not None:
                        info_parts.append(f"Время раунда: {duration}")
                    
                    # Try to load WorkshopItem.json to get publishedFileId
                    workshop_item_file = os.path.join(self.folder_path, "Data", "WorkshopItem.json")
                    if os.path.exists(workshop_item_file):
                        try:
                            with open(workshop_item_file, 'r', encoding='utf-8') as f:
                                workshop_data = json.load(f)
                                if "publishedFileId" in workshop_data:
                                    published_file_id = workshop_data["publishedFileId"]
                                    steam_workshop_link = f"https://steamcommunity.com/sharedfiles/filedetails/?id={published_file_id}"
                                    # Store the link for later use in HTML
                                    self.steam_workshop_link = steam_workshop_link
                                    # Create both Steam protocol link and regular HTTP link
                                    steam_protocol_link = f"steam://url/CommunityFilePage/{published_file_id}"
                                    info_parts.append(f"Ссылка на игру в steam: <a href='{steam_protocol_link}' style='color: #0066cc; text-decoration: underline;'>{published_file_id}</a>")
                        except Exception as e:
                            print(f"Error loading WorkshopItem.json for {self.folder_name}: {e}")
                    
                    # Format the information string
                    if info_parts:
                        info_text = ", ".join(info_parts)
                    else:
                        info_text = "Настройки не найдены"
                    
                    # Update the label with HTML content
                    if hasattr(self, 'mod_info_label'):
                        self.mod_info_label.setText(info_text)
                        
            except Exception as e:
                print(f"Error loading mod settings for {self.folder_name}: {e}")
                if hasattr(self, 'mod_info_label'):
                    self.mod_info_label.setText("Ошибка загрузки настроек")
        else:
            if hasattr(self, 'mod_info_label'):
                self.mod_info_label.setText("Файл настроек не найден")
    
    def update_checkbox_state(self):
        """Update checkbox state based on general_info.json"""
        game_id = os.path.basename(self.folder_path)
        general_info_path = os.path.join(os.path.dirname(__file__), 'general_info.json')
        
        try:
            if os.path.exists(general_info_path):
                with open(general_info_path, 'r', encoding='utf-8') as f:
                    general_info = json.load(f)
                    if 'ids' in general_info and game_id in general_info['ids']:
                        self.checkbox.setChecked(True)
                    else:
                        self.checkbox.setChecked(False)
        except Exception as e:
            print(f"Error reading general_info.json: {e}")
    
    def load_existing_tags(self):
        """Load existing tags for this game from games_info.json"""
        games_info_path = os.path.join(os.path.dirname(__file__), 'games_info.json')
        if os.path.exists(games_info_path):
            try:
                with open(games_info_path, 'r', encoding='utf-8') as f:
                    games_data = json.load(f)
                    for game in games_data:
                        if game['id'] == os.path.basename(self.folder_path):
                            # Handle both string and list formats for tags
                            if 'tags' in game:
                                if isinstance(game['tags'], str):
                                    # If tags is a string, split by comma and strip whitespace
                                    tags = [tag.strip() for tag in game['tags'].split(',') if tag.strip()]
                                elif isinstance(game['tags'], list):
                                    tags = game['tags']
                                else:
                                    tags = []
                                
                                # Add each tag to the UI
                                for tag in tags:
                                    if tag and tag not in self.current_tags:
                                        self.current_tags.add(tag)
                                        self.add_tag_to_ui(tag)
                            
                            # Load description if it exists
                            if 'descr' in game and game['descr']:
                                self.desc_input.setText(game['descr'])
                            break
            except Exception as e:
                print(f"Error loading existing tags: {e}")
    
    def add_tag_to_ui(self, tag):
        """Add a tag to the UI"""
        tag_widget = QFrame()
        tag_widget.setStyleSheet("""
            QFrame {
                background-color: #fff;
                padding: 2px 8px;
            }
        """)
        
        tag_layout = QHBoxLayout(tag_widget)
        tag_layout.setContentsMargins(2, 0, 2, 0)
        tag_layout.setSpacing(5)
        
        tag_label = QLabel(tag)
        tag_label.setStyleSheet("color: #2e7d32; font-size: 12px;")
        
        remove_btn = QPushButton("❎")  # Using a proper multiplication sign instead of X
        remove_btn.setStyleSheet("""
            QPushButton {
  
                border: none;
                font-size: 20px;
 

                min-width: 30px;
                max-width: 30px;
            }
            QPushButton:hover {
            }
        """)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setFixedSize(25, 25)  # Fixed size for the button
        
        # Connect remove button
        remove_btn.clicked.connect(lambda _, t=tag, w=tag_widget: self.remove_tag(t, w))
        
        tag_layout.addWidget(tag_label)
        tag_layout.addWidget(remove_btn)
        
        # Add to layout
        self.selected_tags_layout.addWidget(tag_widget)
    
    def load_game_info(self):
        # Load game info from JSON file
        info_file = os.path.join(os.path.dirname(__file__), "game_info.json")
        if os.path.exists(info_file):
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    all_info = json.load(f)
                    return all_info.get(self.folder_name, {})
            except Exception as e:
                print(f"Error loading game info: {e}")
        return {}
    
    
    def add_tag_to_game(self):
        """Add selected tag to the game and update display"""
        selected_tag = self.tag_dropdown.currentText()
        if selected_tag == "Выберите тег" or selected_tag in self.current_tags:
            return  # Don't add if no tag is selected or tag already exists
        
        # Add to current tags set
        self.current_tags.add(selected_tag)
        
        # Create a tag label with remove button
        tag_widget = QFrame()
        tag_widget.setStyleSheet("""
            QFrame {
                background-color: #fff;
                padding: 0;
            }
        """)
        
        tag_layout = QHBoxLayout(tag_widget)
        tag_layout.setContentsMargins(2, 0, 2, 0)
        tag_layout.setSpacing(5)
        
        tag_label = QLabel(selected_tag)
        tag_label.setStyleSheet("color: #2e7d32; font-size: 12px;")
        
        remove_btn = QPushButton("❎")
        remove_btn.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 20px;
 

                min-width: 30px;
                max-width: 30px;
            }
            QPushButton:hover {

            }
        """)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setFixedSize(25, 25)
        
        # Connect remove button
        remove_btn.clicked.connect(lambda _, t=selected_tag, w=tag_widget: self.remove_tag(t, w))
        
        tag_layout.addWidget(tag_label)
        tag_layout.addWidget(remove_btn)
        
        # Add to layout
        self.selected_tags_layout.addWidget(tag_widget)
        
        # Save the updated tags
        self.save_tags()

    def send_in_trash(self):
        self.save_tags()

    def save_description(self):
        """Save description to games_info.json when Enter is pressed"""
        self.save_tags()
    
    def on_mouse_press(self, event):
        """Handle mouse press events to toggle checkbox when clicking on background"""
        # Only handle left mouse button clicks
        if event.button() == Qt.LeftButton:
            # Toggle the checkbox state
            current_state = self.checkbox.isChecked()
            self.checkbox.setChecked(not current_state)
        
        # Call the default mouse press event handler
        super().mousePressEvent(event)

        self.save_tags()
    
    def remove_tag(self, tag, widget):
        """Remove a tag from the game"""
        if tag in self.current_tags:
            self.current_tags.remove(tag)
            widget.deleteLater()
            self.save_tags()
    
    def toggle_game_id(self, state):
        """Add/remove game ID from general_info.json when checkbox is toggled"""
        game_id = os.path.basename(self.folder_path)
        general_info_path = os.path.join(os.path.dirname(__file__), 'general_info.json')
        
        try:
            # Load current general info
            with open(general_info_path, 'r', encoding='utf-8') as f:
                general_info = json.load(f)
            
            # Initialize ids if it doesn't exist
            if 'ids' not in general_info:
                general_info['ids'] = []
            
            # Add or remove the game ID
            if state == Qt.Checked:
                if game_id not in general_info['ids']:
                    general_info['ids'].append(game_id)
            else:
                if game_id in general_info['ids']:
                    general_info['ids'].remove(game_id)
            
            # Save the updated general info
            with open(general_info_path, 'w', encoding='utf-8') as f:
                json.dump(general_info, f, ensure_ascii=False, indent=2)
                
            # Update the selected games counter in the parent window if it exists
            if hasattr(self.parent(), 'update_selected_counter'):
                self.parent().update_selected_counter()
                
            print(f"{'Added' if state == Qt.Checked else 'Removed'} game ID {game_id} from general_info.json")
                
        except Exception as e:
            print(f"Error updating game selection: {e}")
    
    def save_tags(self):
        """Save current tags to games_info.json"""
        if not hasattr(self, 'folder_path'):
            return
            
        game_data = {
            'id': os.path.basename(self.folder_path),
            'name': self.name_label.text(),
            'tags': list(self.current_tags),
            'descr': self.desc_input.text().strip() if hasattr(self, 'desc_input') else '',
            'top': '',
            'show' : True
        }
        
        # Load existing data
        games_info_path = os.path.join(os.path.dirname(__file__), 'games_info.json')
        try:
            if os.path.exists(games_info_path):
                with open(games_info_path, 'r', encoding='utf-8') as f:
                    games_data = json.load(f)
            else:
                games_data = []
                
            # Check if this game already exists in the data
            game_exists = False
            for i, game in enumerate(games_data):
                if game['id'] == game_data['id']:
                    # Update existing game
                    games_data[i] = game_data
                    game_exists = True
                    break
                    
            if not game_exists:
                # Add new game
                games_data.append(game_data)
                
            # Save back to file
            with open(games_info_path, 'w', encoding='utf-8') as f:
                json.dump(games_data, f, ensure_ascii=False, indent=2)
                
            print(f"Successfully saved tags for game '{game_data['name']}'")
            return True
            
        except Exception as e:
            print(f"Error saving tag: {e}")
            return False
    
class GameBrowser(QMainWindow):
    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        self.setWindowTitle("Mini Games Browser")
        self.setWindowTitle("Mini Games Browser")
        self.setMinimumSize(1700, 800)

        
        # Load tags from general_info.json
        self.tags = self.load_tags()
        
        # Store all games data
        self.all_games = []
        self.filtered_games = []
        self.current_filter_tag = None
        
        # Synchronize and load games info
        self.sync_json_files()
        self.load_games_info()
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Title
        title = QLabel("PummelSorting by 🥩Вотизлове")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0e0; margin-bottom: 10px;")
        self.main_layout.addWidget(title)
        
        # Button row
        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        
        
        # Selected games counter (now clickable)
        self.selected_counter = QPushButton("Выбрано: 0")
        self.selected_counter.setStyleSheet("""
            QPushButton {
                color: #e0e0e0;
                font-size: 14px;
                padding: 5px 10px;
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 4px;
                margin-right: 10px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        self.selected_counter.setCursor(Qt.PointingHandCursor)
        self.selected_counter.clicked.connect(self.show_selected_games)
        
        # Create buttons
        btn_unselected = QPushButton("Убрать галочки")
        btn_go_in_trash = QPushButton("🗙")
        btn_transfer = QPushButton("Выбранные мини-игры добавить в игру")
        btn_transfer_all = QPushButton('Все мини-игры добавить в игру')
        btn_return_here = QPushButton("Вернуть все мини-игры сюда")
        btn_played = QPushButton("Отправить выбранные мини-игры в сыгранные")
        btn_played_return = QPushButton("Вернуть из сыгранных")
        btn_reload = QPushButton("Обновить")

        
        # Style buttons
        button_style = """
            QPushButton {
                padding: 8px 16px;
                background-color: #3a3a3a;
                color: #e0e0e0;
                font-size: 12px;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """
        
        btn_transfer.setStyleSheet(button_style)
        btn_go_in_trash.setStyleSheet(button_style)
        btn_unselected.setStyleSheet(button_style)
        btn_played.setStyleSheet(button_style)
        btn_played_return.setStyleSheet(button_style)
        btn_reload.setStyleSheet(button_style)
        btn_transfer_all.setStyleSheet(button_style)
        btn_return_here.setStyleSheet(button_style)
        
        # Connect buttons
        btn_unselected.clicked.connect(self.uncheck_all_boxes)
        btn_go_in_trash.clicked.connect(self.go_in_trash)
        btn_transfer.clicked.connect(self.transfer_selected_games) 
        btn_played.clicked.connect(self.move_to_played)
        btn_played_return.clicked.connect(self.move_from_played)
        btn_reload.clicked.connect(self.reload_games_info)
        btn_transfer_all.clicked.connect(self.transfer_all_games)
        btn_return_here.clicked.connect(self.return_all_games)
        
        # Add widgets to the row
        button_row.addWidget(self.selected_counter)

        button_row.addWidget(btn_unselected)
        button_row.addWidget(btn_transfer) 
        button_row.addWidget(btn_transfer_all)
        button_row.addWidget(btn_return_here)
        button_row.addWidget(btn_played)
        button_row.addWidget(btn_played_return)
        button_row.addWidget(btn_reload)
        
        button_row.addStretch()
        
        # Add button row to main layout
        self.main_layout.addLayout(button_row)
        
        # Add tag buttons row
        self.tag_buttons_row = QHBoxLayout()
        self.tag_buttons_row.setSpacing(3)
        
        # Store tag buttons for later reference
        self.tag_buttons = {}
        
        # Add 'All' button
        all_btn = QPushButton("С тегами")
        all_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #45a049;
                padding: 5px 0px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        all_btn.setCursor(Qt.PointingHandCursor)
        all_btn.clicked.connect(lambda: self.filter_by_tag(None))
        self.tag_buttons_row.addWidget(all_btn)
        
        # Add 'No Tag' button
        no_tag_btn = QPushButton("Без тега")
        no_tag_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 1px solid #0b7dda;
                padding: 5px 0px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:checked {
                background-color: #0b7dda;
                border: 1px solid #0b5fba;
            }
        """)
        no_tag_btn.setCheckable(True)
        no_tag_btn.setCursor(Qt.PointingHandCursor)
        no_tag_btn.clicked.connect(lambda: self.filter_by_tag(""))
        self.tag_buttons[""] = no_tag_btn
        self.tag_buttons_row.addWidget(no_tag_btn)
        
        # Add tag buttons
        for tag in self.tags:
            tag_btn = QPushButton(tag)
            tag_btn.setStyleSheet("""
                QPushButton {
                    font-size: 11px;
                    background-color: #444;
                    color: white;
                    border: 1px solid #555;
                    padding: 5px 5px;
                    border-radius: 3px;
                    min-width: 50px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
                QPushButton:checked {
                    background-color: #4CAF50;
                    border: 1px solid #45a049;
                }
            """)
            tag_btn.setCheckable(True)
            tag_btn.setCursor(Qt.PointingHandCursor)
            tag_btn.clicked.connect(lambda checked, t=tag: self.filter_by_tag(t))
            self.tag_buttons[tag] = tag_btn
            self.tag_buttons_row.addWidget(tag_btn)
                    
        self.tag_buttons_row.addStretch()
        self.main_layout.addLayout(self.tag_buttons_row)
        
        # Random games controls row
        random_controls_row = QHBoxLayout()
        random_controls_row.setSpacing(10)
        
        # Input field for number of random games
        self.num_random_games = QLineEdit()
        self.num_random_games.setPlaceholderText("Количество")
        self.num_random_games.setFixedWidth(80)
        self.num_random_games.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #555;
                border-radius: 3px;
                background: #3a3a3a;
                color: #e0e0e0;
            }
        """)
        
        # Random games button
        self.random_games_btn = QPushButton("+1 на рандом с каждой категории")
        self.random_games_btn.setStyleSheet(button_style)
        self.random_games_btn.clicked.connect(self.select_one_random_from_each_tag)

        self.random_games_btn_two = QPushButton("+2 на рандом с каждой категории")
        self.random_games_btn_two.setStyleSheet(button_style)
        self.random_games_btn_two.clicked.connect(self.select_two_random_from_each_tag)
        
# Search field for games
        self.search_games_input = QLineEdit()
        self.search_games_input.setPlaceholderText("Поиск мини игр")
        self.search_games_input.setFixedWidth(100)
        self.search_games_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #555;
                border-radius: 3px;
                background: #3a3a3a;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
            QLineEdit:hover {
                cursor: pointer;
            }
        """)

        self.find_game_btn = QPushButton("Найти мини игру")
        self.find_game_btn.setStyleSheet(button_style)
        self.find_game_btn.clicked.connect(self.find_game)
        
        # Connect Enter key press to search
        self.search_games_input.returnPressed.connect(self.find_game)
        
        # Add clear search button
        self.clear_search_btn = QPushButton("Очистить поиск")
        self.clear_search_btn.setStyleSheet(button_style)
        self.clear_search_btn.clicked.connect(self.clear_search)
        
        # Full random button
        self.full_random_btn = QPushButton("Добавить рандомно")
        self.full_random_btn.setStyleSheet(button_style)
        self.full_random_btn.clicked.connect(self.select_random_games)
        
        # Input field for number of new games
        self.num_new_games = QLineEdit()
        self.num_new_games.setPlaceholderText("Количество")
        self.num_new_games.setFixedWidth(80)
        self.num_new_games.setStyleSheet("""
            QLineEdit {
                padding: 7px;
                border: 1px solid #555;
                border-radius: 3px;
                font-size: 12px;
                background: #3a3a3a;
                color: #e0e0e0;
            }
        """)
        
        # Add new games button
        self.new_games_btn = QPushButton("Добавить")
        self.new_games_btn.setStyleSheet(button_style)
        
        # Add widgets to the row
        random_controls_row.addWidget(QLabel("Количество рандомных игр:"))
        random_controls_row.addWidget(self.num_random_games)
        random_controls_row.addWidget(self.full_random_btn)
        random_controls_row.addWidget(self.random_games_btn)
        random_controls_row.addWidget(self.random_games_btn_two)
        random_controls_row.addWidget(self.search_games_input)
        random_controls_row.addWidget(self.find_game_btn)
        random_controls_row.addWidget(self.clear_search_btn)
        random_controls_row.addStretch()
        
        self.main_layout.addLayout(random_controls_row)
        
        # Create scroll area for the list
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #444;
                border-radius: 5px;
                background-color: #2b2b2b;
            }
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #444;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container for the list
        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setSpacing(5)
        self.list_layout.setContentsMargins(10, 10, 10, 10)
        self.list_layout.addStretch()  # Add stretch to push items to top
        
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)
        
        # Load games
        self.load_games()
        
        # Store references to all game widgets
        self.game_widgets = []
        
        # Add status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: #1e1e1e;
                color: #e0e0e0;
                padding: 5px;
                font-size: 12px;
                border-top: 1px solid #444;
            }
        """)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)

    def find_game(self):
        """Find a game by name"""
        try:
            game_name = self.search_games_input.text().strip()
            if not game_name:
                self.statusBar.showMessage("Пожалуйста, введите название мини игры", 3000)
                return
            
            # Get all visible game widgets
            visible_games = []
            for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
                item = self.list_layout.itemAt(i)
                if item and item.widget() and item.widget().isVisible():
                    visible_games.append(item.widget())
            
            # Find the game by name (case-insensitive partial match)
            found_games = []
            for game_widget in visible_games:
                # Check if widget has workshop data with title
                if hasattr(game_widget, 'workshop_data') and game_widget.workshop_data:
                    game_title = game_widget.workshop_data.get('title', '')
                    if game_title and game_name.lower() in game_title.lower():
                        found_games.append(game_widget)
                # Fallback to folder name if no workshop data
                elif hasattr(game_widget, 'folder_name') and game_widget.folder_name:
                    if game_name.lower() in game_widget.folder_name.lower():
                        found_games.append(game_widget)
            
            if found_games:
                # Clear current selection first
                for game_widget in self.game_widgets:
                    if hasattr(game_widget, 'checkbox'):
                        game_widget.checkbox.setChecked(False)
                            
                # Hide all games and show only found ones
                for game_widget in visible_games:
                    if game_widget in found_games:
                        game_widget.setVisible(True)
                    else:
                        game_widget.setVisible(False)
                
                if len(found_games) == 1:
                    # Get the proper title for display
                    game_title = found_games[0].workshop_data.get('title', found_games[0].folder_name) if hasattr(found_games[0], 'workshop_data') and found_games[0].workshop_data else found_games[0].folder_name
                    self.statusBar.showMessage(f"Найдена мини игра: {game_title}", 3000)
                    # Clear search field after successful single result
                    self.search_games_input.clear()
                else:
                    self.statusBar.showMessage(f"Найдено {len(found_games)} мини игр по запросу '{game_name}'", 3000)
            else:
                self.statusBar.showMessage(f"Мини игра по запросу '{game_name}' не найдена", 3000)
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при поиске мини игры: {str(e)}", 3000)
    
    def clear_search(self):
        """Clear search filter and show all games"""
        try:
            # Clear search input
            self.search_games_input.clear()
            
            # Show all games
            for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
                item = self.list_layout.itemAt(i)
                if item and item.widget():
                    item.widget().setVisible(True)
            
            # Clear current selection
            for game_widget in self.game_widgets:
                if hasattr(game_widget, 'checkbox'):
                    game_widget.checkbox.setChecked(False)
            
            # Reset selected games filter state
            if hasattr(self, 'showing_selected_only'):
                self.showing_selected_only = False
                self.update_selected_counter()
            
            self.statusBar.showMessage("Поиск очищен, показаны все игры", 3000)
            
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при очистке поиска: {str(e)}", 3000)
    
    def show_selected_games(self):
        """Show only selected games (with checked checkboxes)"""
        try:
            # Get all visible game widgets
            visible_games = []
            for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
                item = self.list_layout.itemAt(i)
                if item and item.widget() and item.widget().isVisible():
                    visible_games.append(item.widget())
            
            # Count selected games
            selected_count = 0
            for game_widget in visible_games:
                if hasattr(game_widget, 'checkbox') and game_widget.checkbox.isChecked():
                    selected_count += 1
            
            if selected_count == 0:
                self.statusBar.showMessage("Нет выбранных игр", 3000)
                return
            
            # Toggle between showing all games and showing only selected games
            if hasattr(self, 'showing_selected_only') and self.showing_selected_only:
                # Currently showing only selected games, so show all games
                for game_widget in visible_games:
                    game_widget.setVisible(True)
                self.showing_selected_only = False
                self.selected_counter.setText(f"Выбрано: {selected_count}")
                self.statusBar.showMessage("Показаны все игры", 3000)
            else:
                # Currently showing all games, so show only selected games
                for game_widget in visible_games:
                    if hasattr(game_widget, 'checkbox'):
                        if game_widget.checkbox.isChecked():
                            game_widget.setVisible(True)
                        else:
                            game_widget.setVisible(False)
                self.showing_selected_only = True
                self.selected_counter.setText(f"Показать все ({selected_count})")
                self.statusBar.showMessage(f"Показаны {selected_count} выбранных игр", 3000)
            
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при показе выбранных игр: {str(e)}", 3000)

    def select_random_games(self):
        """Randomly select the specified number of games"""
        try:
            # Get the number of games to select
            num_games_text = self.num_random_games.text().strip()
            if not num_games_text.isdigit():
                self.statusBar.showMessage("Пожалуйста, введите корректное число", 3000)
                return
                
            num_to_select = int(num_games_text)
            if num_to_select <= 0:
                self.statusBar.showMessage("Число должно быть больше нуля", 3000)
                return
                
            # Get all visible game widgets, excluding games with unwanted tags
            visible_games = []
            excluded_tags = ["Мусор", "Хард", "Карты"]
            
            for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
                item = self.list_layout.itemAt(i)
                if item and item.widget() and item.widget().isVisible():
                    game_widget = item.widget()
                    # Check if game has any of the excluded tags
                    game_id = os.path.basename(game_widget.folder_path)
                    game_tags = self.get_game_tags(game_id)
                    
                    # Only include games that don't have any of the excluded tags
                    if not any(tag in excluded_tags for tag in game_tags):
                        visible_games.append(game_widget)
                    
            if num_to_select > len(visible_games):
                self.statusBar.showMessage(f"Доступно только {len(visible_games)} игр для выбора (исключая Мусор, Хард, Карты)", 3000)
                return
                
            # Clear current selection
            for game_widget in self.game_widgets:
                if hasattr(game_widget, 'checkbox'):
                    game_widget.checkbox.setChecked(False)
            
            # Select random games
            import random
            selected_games = random.sample(visible_games, num_to_select)
            for game_widget in selected_games:
                if hasattr(game_widget, 'checkbox'):
                    game_widget.checkbox.setChecked(True)
                    
            self.statusBar.showMessage(f"Выбрано {num_to_select} случайных игр (исключая Мусор, Хард, Карты)", 3000)
            
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при выборе случайных игр: {str(e)}", 3000)
    
    def select_one_random_from_each_tag(self):
        """Select one random game from each tag"""
        try:
            # Clear current selection
            for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
                item = self.list_layout.itemAt(i)
                if item and item.widget() and hasattr(item.widget(), 'checkbox'):
                    item.widget().checkbox.setChecked(False)
            
            # Get all visible game widgets
            visible_games = []
            for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
                item = self.list_layout.itemAt(i)
                if item and item.widget() and item.widget().isVisible():
                    visible_games.append(item.widget())
            
            if not visible_games:
                self.statusBar.showMessage("Нет доступных игр для выбора", 3000)
                return
            
            # Group games by tags
            games_by_tag = {}
            for game_widget in visible_games:
                game_id = os.path.basename(game_widget.folder_path)
                game_tags = self.get_game_tags(game_id)
                
                for tag in game_tags:
                    if tag and tag != "Карты":  # Skip empty tags and "Карты" tag
                        if tag == tag != "Хард":
                            if tag == tag != "Мусор":
                                if tag not in games_by_tag:
                                    games_by_tag[tag] = []
                                games_by_tag[tag].append(game_widget)
                
            # Select one random game from each tag
            import random
            selected_count = 0
            
            for tag, games in games_by_tag.items():
                if games:  # If there are games with this tag
                    # Select one random game from this tag
                    selected_game = random.choice(games)
                    if hasattr(selected_game, 'checkbox'):
                        selected_game.checkbox.setChecked(True)
                        selected_count += 1
            
            if selected_count > 0:
                self.statusBar.showMessage(f"Выбрано по одной игре из {selected_count} тегов", 3000)
            else:
                self.statusBar.showMessage("Не удалось выбрать игры по тегам", 3000)
                
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при выборе игр по тегам: {str(e)}", 3000)
    
    def select_two_random_from_each_tag(self):
        """Select two random game from each tag"""
        try:
            # Clear current selection
            for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
                item = self.list_layout.itemAt(i)
                if item and item.widget() and hasattr(item.widget(), 'checkbox'):
                    item.widget().checkbox.setChecked(False)
            
            # Get all visible game widgets
            visible_games = []
            for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
                item = self.list_layout.itemAt(i)
                if item and item.widget() and item.widget().isVisible():
                    visible_games.append(item.widget())
            
            if not visible_games:
                self.statusBar.showMessage("Нет доступных игр для выбора", 3000)
                return
            
            # Group games by tags
            games_by_tag = {}
            for game_widget in visible_games:
                game_id = os.path.basename(game_widget.folder_path)
                game_tags = self.get_game_tags(game_id)
                
                for tag in game_tags:
                    if tag and tag != "Карты":  # Skip empty tags and "Карты" tag
                        if tag == tag != "Хард":
                            if tag == tag != "Мусор":
                                if tag not in games_by_tag:
                                    games_by_tag[tag] = []
                                games_by_tag[tag].append(game_widget)
                
            # Select one random game from each tag
            import random
            selected_count = 0
            
            for tag, games in games_by_tag.items():
                if len(games) >= 2:  # Only if there are at least 2 games with this tag
                    # Select two random games from this tag
                    selected_games = random.sample(games, 2)
                    for game in selected_games:
                        if hasattr(game, 'checkbox'):
                            game.checkbox.setChecked(True)
                            selected_count += 1
                elif games:  # If there's only one game with this tag
                    if hasattr(games[0], 'checkbox'):
                        games[0].checkbox.setChecked(True)
                        selected_count += 1
            
            if selected_count > 0:
                self.statusBar.showMessage(f"Выбрано по одной игре из {selected_count} тегов", 3000)
            else:
                self.statusBar.showMessage("Не удалось выбрать игры по тегам", 3000)
                
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при выборе игр по тегам: {str(e)}", 3000)

    def uncheck_all_boxes(self):
        """Uncheck all checkboxes in the game list"""
        for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
            item = self.list_layout.itemAt(i)
            if item and item.widget() and hasattr(item.widget(), 'checkbox'):
                item.widget().checkbox.setChecked(False)
        self.statusBar.showMessage("Все галочки сняты", 3000)
        
    def reload_games_info(self):
        self.load_games()
        self.statusBar.showMessage("Обновлено", 5000)

    def go_in_trash(self):
        """Move selected game folders to the 'trash' directory"""
        general_info_path = os.path.join(os.path.dirname(__file__), 'general_info.json')
        
        try:
            # Load the general info to get selected game IDs
            with open(general_info_path, 'r', encoding='utf-8') as f:
                general_info = json.load(f)
                
            game_ids = general_info.get('ids', [])
            if not game_ids:
                print("No games selected to move to 'trash'")
                return
                
            # Get the source and destination directories
            source_dir = os.path.dirname(__file__)
            trash_dir = os.path.join(os.path.dirname(__file__), 'trash')
            
            # Create 'trash' directory if it doesn't exist
            os.makedirs(trash_dir, exist_ok=True)
            
            moved_count = 0
            
            for game_id in game_ids[:]:  # Create a copy of the list for iteration
                source_path = os.path.join(source_dir, game_id)
                dest_path = os.path.join(trash_dir, game_id)
                
                if os.path.exists(source_path) and os.path.isdir(source_path):
                    try:
                        # Move the directory
                        os.rename(source_path, dest_path)
                        moved_count += 1
                        self.statusBar.showMessage(f"Moved {game_id} to 'trash' folder", 5000)
                    except Exception as e:
                        self.statusBar.showMessage(f"Error moving {game_id} to 'trash': {e}", 5000)
            
            self.statusBar.showMessage(f"Успешно перенесено {moved_count} из {len(game_ids)} выбранных игр в папку 'trash'", 5000)
            
            # Reload games to reflect changes
            self.load_games()
            
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при перемещении в 'trash': {e}", 5000)

    def move_to_played(self):
        """Move selected game folders to the 'played' directory"""
        general_info_path = os.path.join(os.path.dirname(__file__), 'general_info.json')
        
        try:
            # Load the general info to get selected game IDs
            with open(general_info_path, 'r', encoding='utf-8') as f:
                general_info = json.load(f)
                
            game_ids = general_info.get('ids', [])
            if not game_ids:
                print("No games selected to move to 'played'")
                return
                
            # Get the source and destination directories
            source_dir = os.path.dirname(__file__)
            played_dir = os.path.join(os.path.dirname(__file__), 'played')
            
            # Create 'played' directory if it doesn't exist
            os.makedirs(played_dir, exist_ok=True)
            
            moved_count = 0
            
            for game_id in game_ids[:]:  # Create a copy of the list for iteration
                source_path = os.path.join(source_dir, game_id)
                dest_path = os.path.join(played_dir, game_id)
                
                if os.path.exists(source_path) and os.path.isdir(source_path):
                    try:
                        # Move the directory
                        os.rename(source_path, dest_path)
                        moved_count += 1
                        self.statusBar.showMessage(f"Moved {game_id} to 'played' folder", 5000)
                    except Exception as e:
                        self.statusBar.showMessage(f"Error moving {game_id} to 'played': {e}", 5000)
            
            self.statusBar.showMessage(f"Успешно перенесено {moved_count} из {len(game_ids)} выбранных игр в папку 'played'", 5000)
            
            # Reload games to reflect changes
            self.load_games()
            
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при перемещении в 'сыгранные': {e}", 5000)
            
    def move_from_played(self):
        """Move selected game folders from 'played' back to the main directory"""
        general_info_path = os.path.join(os.path.dirname(__file__), 'general_info.json')
        
        try:
            # Load the general info to get selected game IDs
            with open(general_info_path, 'r', encoding='utf-8') as f:
                general_info = json.load(f)
                
            game_ids = general_info.get('ids', [])
            if not game_ids:
                print("No games selected to move from 'played'")
                return
                
            # Get the source and destination directories
            minigames_dir = os.path.dirname(__file__)
            played_dir = os.path.join(os.path.dirname(__file__), 'played')
            
            moved_count = 0
            
            for game_id in game_ids[:]:  # Create a copy of the list for iteration
                source_path = os.path.join(played_dir, game_id)
                dest_path = os.path.join(minigames_dir, game_id)
                
                if os.path.exists(source_path) and os.path.isdir(source_path):
                    try:
                        # Move the directory
                        os.rename(source_path, dest_path)
                        moved_count += 1
                        self.statusBar.showMessage(f"Перемещено {game_id} из папки 'played' обратно", 5000)
                    except Exception as e:
                        self.statusBar.showMessage(f"Error moving {game_id} from 'played': {e}", 5000)
            
            self.statusBar.showMessage(f"Успешно перемещено {moved_count} из {len(game_ids)} выбранных игр из папки 'played'", 5000)
            
            # Reload games to reflect changes
            self.load_games()
            
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при перемещении из 'сыгранных': {e}", 5000)
    
    def transfer_selected_games(self):
        """Move selected game folders to the parent directory"""
        general_info_path = os.path.join(os.path.dirname(__file__), 'general_info.json')
        
        try:
            # Load the general info to get selected game IDs
            with open(general_info_path, 'r', encoding='utf-8') as f:
                general_info = json.load(f)
                
            game_ids = general_info.get('ids', [])
            if not game_ids:
                print("No games selected for transfer")
                return
                
            # Get the parent directory (one level up from minigames)
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            source_dir = os.path.dirname(__file__)
            
            moved_count = 0
            
            for game_id in game_ids[:]:  # Create a copy of the list for iteration
                source_path = os.path.join(source_dir, game_id)
                dest_path = os.path.join(parent_dir, game_id)
                
                if os.path.exists(source_path) and os.path.isdir(source_path):
                    try:
                        # Move the directory
                        os.rename(source_path, dest_path)
                        moved_count += 1
                        self.statusBar.showMessage(f"Перемещено {game_id} в {parent_dir}", 5000)
                    except Exception as e:
                        self.statusBar.showMessage(f"Error moving {game_id}: {e}", 5000)
            
            self.statusBar.showMessage(f"Успешно перемещено {moved_count} из {len(game_ids)} выбранных игр", 5000)

            self.load_games()
            
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка при перемещении: {e}", 5000)
    
    def return_all_games(self):
        """Move all game folders from parent directory back to minigames directory"""
        # Get the parent directory (where the games are currently located)
        parent_dir = os.path.dirname(self.root_path)
    
        # Get all game folders in the parent directory
        game_folders = [f for f in os.listdir(parent_dir) 
                   if os.path.isdir(os.path.join(parent_dir, f)) 
                   and f.isdigit()  # Only directories with numeric names (game IDs)
                   and f != os.path.basename(self.root_path)]  # Skip the minigames directory itself
    
        if not game_folders:
            self.statusBar.showMessage("Нет игр для возврата в папку minigames", 3000)
            return
        
        # Move each game folder to the minigames directory
        moved_count = 0
        for game_id in game_folders:
            source_path = os.path.join(parent_dir, game_id)
            dest_path = os.path.join(self.root_path, game_id)
        
            if os.path.exists(source_path) and os.path.isdir(source_path):
                try:
                    # Skip if destination already exists
                    if not os.path.exists(dest_path):
                        os.rename(source_path, dest_path)
                        moved_count += 1
                except Exception as e:
                    self.statusBar.showMessage(f"Ошибка при переносе {game_id}: {str(e)}", 5000)
                    continue
    
        if moved_count > 0:
            self.statusBar.showMessage(f"Успешно возвращено {moved_count} игр в папку minigames", 5000)
            # Reload the game list to reflect changes
            self.load_games()
        else:
            self.statusBar.showMessage("Не удалось вернуть ни одной игры. Возможно, все игры уже находятся в папке minigames.", 5000)

    def transfer_all_games(self):
        """Move all game folders to the parent directory"""
        # Get the parent directory (where we'll move the games to)
        parent_dir = os.path.dirname(self.root_path)
        
        # Get all game folders in the current directory
        game_folders = [f for f in os.listdir(self.root_path) 
                       if os.path.isdir(os.path.join(self.root_path, f)) 
                       and f != 'played'  # Skip the 'played' directory
                       and not f.startswith('.')]  # Skip hidden directories
        
        if not game_folders:
            self.statusBar.showMessage("Нет игр для переноса", 3000)
            return
            
        # Move each game folder to the parent directory
        moved_count = 0
        for game_id in game_folders:
            source_path = os.path.join(self.root_path, game_id)
            dest_path = os.path.join(parent_dir, game_id)
            
            if os.path.exists(source_path) and os.path.isdir(source_path):
                try:
                    # Skip if destination already exists
                    if not os.path.exists(dest_path):
                        os.rename(source_path, dest_path)
                        moved_count += 1
                except Exception as e:
                    self.statusBar.showMessage(f"Ошибка при переносе {game_id}: {str(e)}", 5000)
                    continue
        
        if moved_count > 0:
            self.statusBar.showMessage(f"Успешно перенесено {moved_count} игр в основную директорию", 5000)
            # Reload the game list to reflect changes
            self.load_games()
        else:
            self.statusBar.showMessage("Не удалось перенести ни одной игры. Возможно, все игры уже находятся в основном каталоге.", 5000)
    
    def save_games_info(self):
        """Save all games info to games_info.json"""
        games_data = []
        
        for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
            item = self.list_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ThumbnailWidget):
                widget = item.widget()
                selected_tag = widget.tag_dropdown.currentText()
                game_data = {
                    'id': os.path.basename(widget.folder_path),
                    'name': widget.name_label.text(),
                    'tags': selected_tag if selected_tag != "Выберите тег" else "",
                    'descr': '',
                    'top' : '',
                    'show' : True
                }
                games_data.append(game_data)
        
        # Save to file
        try:
            output_file = os.path.join(os.path.dirname(__file__), 'games_info.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(games_data, f, ensure_ascii=False, indent=2)
            print(f"Successfully saved {len(games_data)} games to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving games info: {e}")
            return False
    
    def sync_json_files(self):
        """Synchronize data between general_info.json and games_info.json"""
        general_info_path = os.path.join(os.path.dirname(__file__), 'general_info.json')
        games_info_path = os.path.join(os.path.dirname(__file__), 'games_info.json')
        
        try:
            # Load existing data
            if os.path.exists(general_info_path):
                with open(general_info_path, 'r', encoding='utf-8') as f:
                    general_info = json.load(f)
            else:
                general_info = {'tags': [], 'ids': []}
                
            # Load existing games info or create new list
            if os.path.exists(games_info_path):
                with open(games_info_path, 'r', encoding='utf-8') as f:
                    games_info = json.load(f)
            else:
                games_info = []
                
            # Convert games_info to a dictionary for easier updates
            games_dict = {game['id']: game for game in games_info}
            
            # Scan for games in the root directory and update names if needed
            for item in os.listdir(self.root_path):
                item_path = os.path.join(self.root_path, item)
                if os.path.isdir(item_path) and item != 'played':
                    # If game is not in games_info, add it
                    if item not in games_dict:
                        # Try to load WorkshopItem.json for game info
                        workshop_path = os.path.join(item_path, 'WorkshopItem.json')
                        game_name = item  # Default to folder name
                        
                        if os.path.exists(workshop_path):
                            try:
                                with open(workshop_path, 'r', encoding='utf-8') as f:
                                    workshop_data = json.load(f)
                                    if 'title' in workshop_data:
                                        game_name = workshop_data['title']
                            except Exception as e:
                                print(f"Error loading WorkshopItem.json for {item}: {e}")
                        
                        # Add new game to games_dict
                        games_dict[item] = {
                            'id': item,
                            'name': game_name,
                            'tags': [],
                            'descr': '',
                            'top': '',
                            'show': True
                        }
                    else:
                        # Update game name if it's different from WorkshopItem.json
                        workshop_path = os.path.join(item_path, 'WorkshopItem.json')
                        if os.path.exists(workshop_path):
                            try:
                                with open(workshop_path, 'r', encoding='utf-8') as f:
                                    workshop_data = json.load(f)
                                    if 'title' in workshop_data and workshop_data['title'] != games_dict[item]['name']:
                                        games_dict[item]['name'] = workshop_data['title']
                            except Exception as e:
                                print(f"Error updating name from WorkshopItem.json for {item}: {e}")
            
            # Convert back to list and sort by name
            updated_games_info = sorted(games_dict.values(), key=lambda x: x['name'].lower())
            
            # Save updated games_info
            with open(games_info_path, 'w', encoding='utf-8') as f:
                json.dump(updated_games_info, f, ensure_ascii=False, indent=2)
                
            # Ensure general_info has required fields
            if 'tags' not in general_info:
                general_info['tags'] = []
            if 'ids' not in general_info:
                general_info['ids'] = []
                
            # Save updated general_info
            with open(general_info_path, 'w', encoding='utf-8') as f:
                json.dump(general_info, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error synchronizing JSON files: {e}")
    
    def load_tags(self):
        """Load tags from general_info.json"""
        try:
            with open(os.path.join(os.path.dirname(__file__), 'general_info.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('tags', [])
        except Exception as e:
            print(f"Error loading tags: {e}")
            return []
    
    def load_games_info(self):
        """Load games info from games_info.json"""
        games_info_path = os.path.join(os.path.dirname(__file__), 'games_info.json')
        try:
            if os.path.exists(games_info_path):
                with open(games_info_path, 'r', encoding='utf-8') as f:
                    self.all_games = json.load(f)
            else:
                self.all_games = []
        except Exception as e:
            print(f"Error loading games info: {e}")
            self.all_games = []
    
    def get_game_tags(self, game_id):
        """Get tags for a specific game"""
        for game in self.all_games:
            if game.get('id') == game_id:
                tags = game.get('tags', '')
                if isinstance(tags, str):
                    return [tags] if tags else []
                return tags if tags else []
        return []
    
    def filter_by_tag(self, tag):
        """Filter games by tag"""
        self.current_filter_tag = tag
        
        # Update button states
        for btn_tag, btn in self.tag_buttons.items():
            btn.setChecked(btn_tag == tag)
            
        self.update_game_display()
        
        if tag == self.current_filter_tag:
            self.current_filter_tag = None
            # Reset all tag buttons
            for btn in self.tag_buttons.values():
                btn.setChecked(False)

    def update_tag_button_counts(self):
        """Update the count of checked games for each tag"""
        # Initialize counters for each tag
        tag_counts = {tag: 0 for tag in self.tags}
        
        # Count checked games for each tag
        for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
            item = self.list_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ThumbnailWidget):
                if item.widget().checkbox.isChecked():
                    game_id = os.path.basename(item.widget().folder_path)
                    game_tags = self.get_game_tags(game_id)
                    for tag in game_tags:
                        if tag in tag_counts:
                            tag_counts[tag] += 1
        
        # Update button texts
        for tag, btn in self.tag_buttons.items():
            if tag:  # Skip empty tag (handled by "Без тега" button)
                count = tag_counts.get(tag, 0)
                btn_text = f"{tag} ({count})" if count > 0 else tag
                btn.setText(btn_text)
    
    def update_selected_counter(self):
        """Update the selected games counter and tag button counts"""
        count = 0
        for i in range(self.list_layout.count() - 1):  # -1 to skip the stretch
            item = self.list_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ThumbnailWidget):
                if item.widget().checkbox.isChecked():
                    count += 1
        self.selected_counter.setText(f"Выбрано: {count}")
        self.update_tag_button_counts()
    
    def update_game_display(self):
        """Update the game display based on current filter"""
        # Store the current scroll position
        scroll_bar = self.scroll.verticalScrollBar()
        scroll_position = scroll_bar.value() if scroll_bar else 0
        
        # Clear existing items
        while self.list_layout.count() > 0:  # Remove all items including stretch
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add stretch back
        self.list_layout.addStretch()
        
        # Get filtered game paths
        if self.current_filter_tag is None:
            # Show only games with at least one tag, excluding unwanted tags
            filtered_paths = []
            excluded_tags = ["Мусор", "Хард", "Карты"]
            for item in os.listdir(self.root_path):
                item_path = os.path.join(self.root_path, item)
                if os.path.isdir(item_path) and item != 'played':
                    game_tags = self.get_game_tags(item)
                    if game_tags and any(game_tags):
                        # Check if game has any of the excluded tags
                        if not any(tag in excluded_tags for tag in game_tags):
                            filtered_paths.append(item_path)
        elif self.current_filter_tag == "":
            filtered_paths = []
            for item in os.listdir(self.root_path):
                item_path = os.path.join(self.root_path, item)
                if os.path.isdir(item_path) and item != 'played':
                    game_tags = self.get_game_tags(item)
                    if not game_tags or (isinstance(game_tags, list) and not any(game_tags)):
                        filtered_paths.append(item_path)
        else:
            filtered_paths = []
            for item in os.listdir(self.root_path):
                item_path = os.path.join(self.root_path, item)
                if os.path.isdir(item_path) and item != 'played':
                    game_tags = self.get_game_tags(item)
                    if self.current_filter_tag in game_tags:
                        filtered_paths.append(item_path)
        
        # Add filtered games
        for game_path in filtered_paths:
            preview_path = os.path.join(game_path, "Data", "Preview.jpg")
            if os.path.exists(preview_path):
                game_widget = ThumbnailWidget(game_path, preview_path, self.tags)
                # Connect checkbox state change to update counters
                game_widget.checkbox.stateChanged.connect(self.update_selected_counter)
                # Update tag button counts when a game is checked/unchecked
                game_widget.checkbox.stateChanged.connect(self.update_tag_button_counts)
                self.list_layout.insertWidget(self.list_layout.count() - 1, game_widget)
        
        # Restore scroll position
        if scroll_bar:
            scroll_bar.setValue(scroll_position)
        
        # Update the counter
        self.update_selected_counter()
    
    def load_games(self):
        """Load all games from the root directory"""
        # Load games info first
        self.load_games_info()
        # Then update the display
        self.update_game_display()


def main():
    import datetime
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Get the directory where the script is located
    root_path = os.path.dirname(os.path.abspath(__file__))
    
    browser = GameBrowser(root_path)
    browser.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()