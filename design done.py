import pygame
import time
import random
import math


class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, text_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
    
    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)  # Rounded corners
        text_surf = self.font.render(self.text, True, self.text_color)
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()

########################################

class ImageButton(Button):
    def __init__(self, x, y, width, height, image, action=None):
        # Initialize the parent class (Button) with default values
        super().__init__(x, y, width, height, text='', font=None, color=None, hover_color=None, text_color=None, action=action)
        self.image = image  # Store the image for the button
    
    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        
        # No need to change the hover color logic since image is the main element
        if self.rect.collidepoint(mouse_pos):
            # Optionally, you can add a hover effect (e.g., scale or outline) here
            pass
        
        # Draw the image scaled to the button size
        button_image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
        screen.blit(button_image, self.rect.topleft)  # Draw the image at the button's position

########################################

########################################

class Screen:
    def __init__(self, buttons, home_button):
        self.buttons = buttons
        self.home_button = home_button
    
    def draw(self, screen):
        ###screen.fill((178, 172, 136))  # original grey
        screen.fill((114,165,119))
        for button in self.buttons:
            button.draw(screen)
        self.home_button.draw(screen)
    
    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)
        self.home_button.handle_event(event)

class ScreenManager:
    def __init__(self):
        self.screens = {}
        self.current_screen = None
    
    def add_screen(self, name, screen):
        self.screens[name] = screen
    
    def set_screen(self, name):
        if name in self.screens:
            self.current_screen = name
    
    def draw(self, screen):
        if self.current_screen:
            self.screens[self.current_screen].draw(screen)
    
    def handle_event(self, event):
        if self.current_screen:
            self.screens[self.current_screen].handle_event(event)

########################################

########################################

########################################

class ScrollingTaskList:
    def __init__(self, x, y, width, height, font, task_list, max_items, scroll_speed=2):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.task_list = task_list  # List of Task objects
        self.max_items = max_items  # Max items to display at once
        self.scroll_speed = scroll_speed  # Speed of scrolling
        self.offset = 0  # Vertical offset to manage scrolling
        self.selected_task = None  # To track the selected task
        self.editing_task = None  # To track the task being edited
        self.editing_text = ""  # The text being typed for editing
        self.last_click_time = 0  # Track the time of the last click
        self.double_click_threshold = 300  # 300 ms threshold for double click
        self.double_click_task = None  # Task that was double-clicked (if any)
    
    def draw(self, screen):
        """Draw the task list and handle scrolling."""
        # Draw the background for the list
        pygame.draw.rect(screen, (158, 198, 162), self.rect)  # Light gray background (200,200,200)
        
        # Calculate how many tasks can fit in the list
        item_height = self.font.get_height()
        visible_tasks = self.task_list[self.offset:self.offset + self.max_items]

        # Draw each visible task
        for i, task in enumerate(visible_tasks):
            # Set the text color based on task completion
            text_color = (0, 0, 255) if task.complete else (0, 0, 0)  # Blue if complete, black if not
            text_surf = self.font.render(task.text, True, text_color)  # Task text with the appropriate color
            task_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10 + i * item_height, self.rect.width - 20, item_height)
            pygame.draw.rect(screen, (255, 255, 255), task_rect)  # White background for each task
            screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 10 + i * item_height))
            
            # Highlight selected task
            if self.selected_task == i + self.offset:
                pygame.draw.rect(screen, (0, 255, 0), task_rect, 3)  # Green border for the selected task

        # If editing, draw the text box for editing
        if self.editing_task is not None:
            edit_box = pygame.Rect(self.rect.x + 10, self.rect.y + 10 + (self.editing_task - self.offset) * item_height, self.rect.width - 20, item_height)
            pygame.draw.rect(screen, (255, 255, 255), edit_box)  # White background for input box
            input_surf = self.font.render(self.editing_text, True, (0, 0, 0))
            screen.blit(input_surf, (edit_box.x, edit_box.y))  # Draw the input text inside the box
            pygame.draw.rect(screen, (0, 255, 0), edit_box, 3)

    def handle_event(self, event):
        """Handle key events for scrolling and task selection."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.scroll_down()
                self.selected_task = None  # Reset selected task
                self.editing_task = None  # Stop editing
            elif event.key == pygame.K_UP:
                self.scroll_up()
                self.selected_task = None  # Reset selected task
                self.editing_task = None  # Stop editing
            elif event.key == pygame.K_RETURN:  # Save the edited task
                self.save_task()
                self.editing_task = None  # Stop editing
            elif event.key == pygame.K_BACKSPACE and self.editing_text:  # Handle backspace
                self.editing_text = self.editing_text[:-1]
            elif event.unicode:  # Handle character input
                if len(self.editing_text) < 35:  # Add new character only if length is less than 35
                    self.editing_text += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.select_task(event.pos)
    
    def scroll_down(self):
        """Scroll down in the list."""
        if self.offset + self.max_items < len(self.task_list):
            self.offset += self.scroll_speed
        else:
            self.offset = len(self.task_list) - self.max_items  # Stop scrolling at the bottom
    
    def scroll_up(self):
        """Scroll up in the list.""" 
        if self.offset > 0:
            self.offset -= self.scroll_speed
        else:
            self.offset = 0  # Stop scrolling at the top
    
    def select_task(self, mouse_pos):
        """Select a task when clicked."""
        item_height = self.font.get_height()
        index = (mouse_pos[1] - self.rect.y - 10) // item_height
        if 0 <= index < self.max_items:
            task_index = index + self.offset
            
            current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
            if current_time - self.last_click_time <= self.double_click_threshold:
                # Double-click detected, toggle the complete status
                task = self.task_list[task_index]
                task.toggle_complete()  # Toggle the task's completion status
            else:
                # Single-click detected, just select the task
                self.selected_task = task_index
                self.start_editing_task(task_index)

            self.last_click_time = current_time  # Update last click time
    
    def start_editing_task(self, task_index):
        """Start editing a task."""
        self.editing_task = task_index
        self.editing_text = self.task_list[task_index].text  # Pre-fill the input box with the current task
    
    def save_task(self):
        """Save the edited task."""
        if self.editing_task is not None:
            self.task_list[self.editing_task].text = self.editing_text  # Update the task's text
            self.editing_task = None  # Stop editing
            self.editing_text = ""  # Clear the text input field

    def add_task(self, task):
        """Add a task to the list."""
        self.task_list.append(Task(task))  # Add a new Task object
    
    def remove_task(self):
        """Remove the selected task from the list."""
        if self.selected_task is not None:
            self.task_list.pop(self.selected_task)
            self.selected_task = None  # Reset selected task
            self.editing_task = None  # Stop editing

class Task:
    def __init__(self, text):
        self.text = text
        self.complete = False  # Attribute to track if the task is complete
        self.bingo_marked = False
        self.square = None


    def toggle_complete(self):
        """Toggle the completion status of the task."""
        self.complete = not self.complete

        
########################################

########################################

########################################


class Reward:
    def __init__(self, text):
        self.text = text  # Reward description
        self.complete = False  # Completion status of the reward (True if redeemed)

    def toggle_complete(self):
        """Toggle the completion status of the reward."""
        self.complete = not self.complete


class ScrollingRewardList(ScrollingTaskList):
    def __init__(self, x, y, width, height, font, reward_list, max_items, scroll_speed=2):
        # Reuse the ScrollingTaskList and its functionality
        super().__init__(x, y, width, height, font, reward_list, max_items, scroll_speed)
        self.reward_list = self.task_list  # Reuse the task list
    
    def draw(self, screen):
        """Draw the reward list and handle scrolling."""
        # Call the draw method of ScrollingTaskList to handle the drawing
        super().draw(screen)
        
        # Modify text drawing for Rewards - strike-through if complete
        item_height = self.font.get_height()
        visible_rewards = self.reward_list[self.offset:self.offset + self.max_items]

        for i, reward in enumerate(visible_rewards):
            text_color = (0, 0, 255) if reward.complete else (0, 0, 0)  # Blue if complete, black if not
            
            if reward.complete:
                # Draw strikethrough for completed rewards
                pygame.draw.line(screen, text_color, 
                                 (self.rect.x + 10, self.rect.y + 10 + i * item_height + item_height // 2),
                                 (self.rect.x + self.rect.width - 10, self.rect.y + 10 + i * item_height + item_height // 2), 
                                 2)  # Strikethrough line
            
            # Use the base task rendering code
            text_surf = self.font.render(reward.text, True, text_color)  
            reward_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10 + i * item_height, self.rect.width - 20, item_height)
            pygame.draw.rect(screen, (255, 255, 255), reward_rect)  # White background for each reward
            screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 10 + i * item_height))
        
            # Highlight selected reward
            if self.selected_task == i + self.offset:
                pygame.draw.rect(screen, (0, 255, 0), reward_rect, 3)  # Green border for the selected reward
        
        # If editing, draw the text box for editing
        if self.editing_task is not None:
            edit_box = pygame.Rect(self.rect.x + 10, self.rect.y + 10 + (self.editing_task - self.offset) * item_height, self.rect.width - 20, item_height)
            pygame.draw.rect(screen, (255, 255, 255), edit_box)  # White background for input box
            input_surf = self.font.render(self.editing_text, True, (0, 0, 0))
            screen.blit(input_surf, (edit_box.x, edit_box.y))  # Draw the input text inside the box
            pygame.draw.rect(screen, (0, 255, 0), edit_box, 3)
    
    def select_reward(self, mouse_pos):
        """Select a reward when clicked."""
        item_height = self.font.get_height()
        index = (mouse_pos[1] - self.rect.y - 10) // item_height
        if 0 <= index < self.max_items:
            reward_index = index + self.offset

            # Single-click detected, just select the reward and start editing it
            self.selected_task = reward_index
            self.start_editing_task(reward_index)
    
    def start_editing_task(self, reward_index):
        """Start editing a reward."""
        self.editing_task = reward_index
        self.editing_text = self.reward_list[reward_index].text  # Pre-fill the input box with the current reward text
    
    def save_task(self):
        """Save the edited reward."""
        if self.editing_task is not None:
            self.reward_list[self.editing_task].text = self.editing_text  # Update the reward's text
            self.editing_task = None  # Stop editing
            self.editing_text = ""  # Clear the text input field



########################################

########################################

########################################

            

class SpinningWheel:
    def __init__(self, x, y, radius, rewards):
        self.x = x
        self.y = y
        self.radius = radius
        self.tasks = tasks
        self.angle = 0
        self.spinning = False
        self.spin_speed = 0
        self.selected_task = None
    
    def start_spin(self):
        if not self.spinning:
            self.spinning = True
            self.spin_speed = random.uniform(20, 30)  # Random speed
    
    def update(self):
        if self.spinning:
            self.angle += self.spin_speed
            self.spin_speed *= 0.98  # Gradually slow down
            if abs(self.spin_speed) < 0.5:  # Use absolute value for smoother stop
                self.spinning = False
                self.select_task()
    
    def select_task(self):
        segment_angle = 360 / len(self.tasks)
        selected_index = int((-self.angle % 360) // segment_angle)
        self.selected_task = self.tasks[selected_index]
    
    def draw(self, screen):
        segment_angle = 360 / len(self.tasks)
        for i in range(len(self.tasks)):
            start_angle = math.radians(self.angle + i * segment_angle)
            end_angle = math.radians(self.angle + (i + 1) * segment_angle)
            color = COLORS[i % len(COLORS)]
            
            pygame.draw.polygon(screen, color, [
                (self.x, self.y),
                (self.x + self.radius * math.cos(start_angle), self.y + self.radius * math.sin(start_angle)),
                (self.x + self.radius * math.cos(end_angle), self.y + self.radius * math.sin(end_angle))
            ])
        
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius, 3)
        
        pygame.draw.polygon(screen, BLACK, [
            (self.x, self.y - self.radius - 10),
            (self.x - 10, self.y - self.radius + 10),
            (self.x + 10, self.y - self.radius + 10)
        ])


########################################

########################################

########################################


def add_newline_between_words(input_string):
    words = input_string.split()  # Split the string into a list of words
    return '\n'.join(words)  # Join the words with a newline character

def remove_newlines_and_replace_with_spaces(input_string):
    return input_string.replace('\n', ' ')

class BingoSquare(Button):
    def __init__(self, x, y, size, text, font, action=None):
        super().__init__(x, y, size, size, text, font, (255, 255, 255), (200, 200, 200), (0, 0, 0), action)
        self.marked = False  # Whether the square has been marked
        self.index = 0
    
    def draw(self, screen):
        # Draw the square with the marked status
        color = (0, 255, 0) if self.marked else (255, 255, 255)  # Green if marked, white if not
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)  # Border

        lines = self.text.split('\n')
        total_text_height = sum(self.font.size(line)[1] for line in lines)
        current_y = self.rect.top + (self.rect.height - total_text_height) // 2
        for line in lines:
            text_surf = self.font.render(line, True, self.text_color)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, current_y))
            screen.blit(text_surf, text_rect)
            current_y += self.font.size(line)[1]
        

    def toggle(self):
        # Toggle the marked state of the square
        self.marked = not self.marked

        if self.marked:
            for z in range (len(tasks)):
                if z == self.index:
                    tasks[z].bingo_marked = True
        else:
            for z in range (len(tasks)):
                if z == self.index:
                    tasks[z].bingo_marked = False



class BingoBoard:
    def __init__(self, x, y, size, font):
        self.x = x
        self.y = y
        self.size = size
        self.font = font
        self.squares = []  # List of BingoSquare objects

        # Bingo board structure (5x5)
        #numbers = random.sample(range(1, 76), 16)  # Random numbers 1-75, 24 numbers for the board

        # Create Bingo squares and add them to the list
        for i in range(4):
            for j in range(4):
                if len(tasks) - 1 >= (i * 4 + j):
                    text = add_newline_between_words(tasks[i * 4 + j].text)
                else:
                    text = "-"
                square = BingoSquare(self.x + j * (size + 10), self.y + i * (size + 10), size, text, self.font, self.toggle_square)

                if len(tasks) - 1 >= (i * 4 + j):
                    tasks[i * 4 + j].square = square
                    square.index = (i * 4 + j)
                else:
                    square.marked = True
                
                self.squares.append(square)

    def toggle_square(self):
        # Handle toggling square on click
        pass

    def draw(self, screen):
        # Draw all the squares
        for square in self.squares:
            square.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for square in self.squares:
                if square.rect.collidepoint(event.pos):
                    square.toggle()  # Toggle the marked state when clicked

    def refresh_board(self):
        self.squares = []
        for i in range(4):
            for j in range(4):
                if len(tasks) - 1 >= (i * 4 + j):
                    text = add_newline_between_words(tasks[i * 4 + j].text)
                else:
                    text = "-"

                square = BingoSquare(self.x + j * (self.size + 10), self.y + i * (self.size + 10), self.size, text, self.font, self.toggle_square)
                if len(tasks) - 1 >= (i * 4 + j):
                    if tasks[i * 4 + j].bingo_marked == True:
                        square.marked = True
                    square.index = (i * 4 + j)
                else:
                    square.marked = True
                
                self.squares.append(square)






class BingoScreen(Screen):
    def __init__(self, bingo_board, home_button, reward_button, vine_button):
        super().__init__([], home_button)
        self.bingo_board = bingo_board
        self.reward_button = reward_button
        self.vine_button = vine_button

    def draw(self, screen):
        self.bingo_board.refresh_board()
        screen.fill((114,165,119)) 
        self.bingo_board.draw(screen)
        self.home_button.draw(screen)
        self.reward_button.draw(screen)
        self.vine_button.draw(screen)

    def handle_event(self, event):
        self.bingo_board.handle_event(event)
        self.home_button.handle_event(event)
        self.reward_button.handle_event(event)

##################################

##################################

##################################


# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((600, 400))
font = pygame.font.Font(None, 36)
bingoFont = pygame.font.Font(None,18)
screen_manager = ScreenManager()

# Constants
WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]

# Create tasks
# Create example tasks
tasks = [
    Task("Go Shopping"),
    Task("Clean my Room"),
    Task("Finish Coursework"),
    Task("Call mom"),
    Task("Go on a walk"),
    Task("Read a book"),
    Task("Write some code"),
    Task("Pay bills"),
    Task("Plan weekend trip"),
    Task("Check emails"),
    Task("Walk the dog"),
    Task("Organize workspace"),
    Task("Fix bugs in the project"),
    Task("Check trains")
]


# Create example rewards (similar to tasks)
rewards = [
    Reward("Have a Hot Chocolate"),
    Reward("Takeaway tonight"),
    Reward("Movie night"),
    Reward("Weekend trip"),
    Reward("Spa evening"),
    Reward("Gift card"),
    Reward("Chocolate"),
    Reward("Watch YouTube"),
]




# Function to return to the menu screen
def go_to_menu():
    screen_manager.set_screen("Menu")
    pygame.display.set_caption('Menu')

# Function to go to To-Do List screen
def go_to_todo():
    screen_manager.set_screen("To-Do List")
    pygame.display.set_caption('To-Do List')

# Function to go to Rewards screen
def go_to_rewards():
    screen_manager.set_screen("Rewards")
    pygame.display.set_caption('Rewards List')

# Function to go to Bingo screen
def go_to_bingo():
    screen_manager.set_screen("Bingo")
    pygame.display.set_caption('Bingo Board')
    bingo_board = BingoBoard(130, 30, 80, bingoFont)
    bingo_screen = (bingo_board, home_button, reward_button, vine_button2)

# Function to go to Randomiser screen
def go_to_randomiser():
    screen_manager.set_screen("Randomiser")
    pygame.display.set_caption('Randomiser')
    generate_randomiser_page()

def random_reward():
    # Define pop-up size and position
    popup_width, popup_height = 300, 150
    popup_x, popup_y = (screen.get_width() - popup_width) // 2, (screen.get_height() - popup_height) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

    selected_reward = random.choice(rewards).text

    # Create an "OK" button to close the pop-up
    button = Button(popup_x + 100, popup_y + 90, 100, 40, "OK", font, (0, 200, 0), (0, 255, 0), (255, 255, 255))

    running = True
    while running:
        screen.fill((114,165,119))  # Background color

        # Draw the pop-up rectangle
        pygame.draw.rect(screen, (255, 255, 255), popup_rect)
        pygame.draw.rect(screen, (0, 0, 0), popup_rect, 3)  # Border

        # Render reward text
        text_surf = font.render(selected_reward, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(popup_x + popup_width // 2, popup_y + 40))
        screen.blit(text_surf, text_rect)

        # Draw the button
        button.draw(screen)

        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            button.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button.rect.collidepoint(event.pos):  # Close pop-up when "OK" is clicked
                    running = False


############# ART #################

title_image = pygame.image.load('title_image.png').convert_alpha()
title_button = ImageButton(x=90,y=5,width=450,height=100,image=title_image, action= None)

logo_image = pygame.image.load('logo_image.png').convert_alpha()
logo_button = ImageButton(x=430,y=150,width=180,height=300,image=logo_image, action= None)
logo_button2 = ImageButton(x=450,y=150,width=180,height=300,image=logo_image, action= None)

vine_image = pygame.image.load('vine_image.png').convert_alpha()
vine_button = ImageButton(x=-30,y=20,width=200,height=450,image=vine_image, action= None)
vine_button2 = ImageButton(x=-60,y=20,width=200,height=450,image=vine_image, action= None)

##################################

menu_buttons = [
    Button(200, 120, 200, 50, "To-Do List", font, (255, 255, 255), (200, 200, 200), (0, 0, 0), go_to_todo),
    Button(200, 180, 200, 50, "Rewards", font, (255, 255, 255), (200, 200, 200), (0, 0, 0), go_to_rewards),
    Button(200, 240, 200, 50, "Bingo", font, (255, 255, 255), (200, 200, 200), (0, 0, 0), go_to_bingo),
    Button(200, 300, 200, 50, "Randomiser", font, (255, 255, 255), (200, 200, 200), (0, 0, 0), go_to_randomiser),
    title_button,
    logo_button,
    vine_button
]

#home_button = Button(10, 10, 50, 50, "🏠", font, (255, 255, 255), (200, 200, 200), (0, 0, 0), go_to_menu)

house_image = pygame.image.load('house_image.png').convert_alpha()
home_button = ImageButton(x=5,y=5,width=50,height=50,image=house_image, action= go_to_menu)

title_image = pygame.image.load('title_image.png').convert_alpha()
title_button = ImageButton(x=50,y=5,width=300,height=50,image=title_image, action= None)

reward_button = Button(490, 340, 100, 50, "Reward", font, (255, 255, 255), (200, 200, 200), (0, 0, 0), random_reward)


bingo_board = BingoBoard(130, 30, 80, bingoFont)
bingo_screen = BingoScreen(bingo_board, home_button, reward_button, vine_button2)

# Adding screens with buttons and home button
screen_manager.add_screen("Menu", Screen(menu_buttons, home_button))


screen_manager.add_screen("Bingo", bingo_screen)  # Add Bingo screen


screen_manager.add_screen("Randomiser", Screen([vine_button, logo_button2], home_button))

# Set initial screen to Menu
screen_manager.set_screen("Menu")
pygame.display.set_caption('Menu')


# Create a ScrollingTaskList for the To-Do List screen
todo_list = ScrollingTaskList(50, 50, 500, 300, font, tasks, max_items=7)


# Create the ScrollingRewardList for the Rewards page
rewards_list = ScrollingRewardList(50, 50, 500, 300, font, rewards, max_items=7)


# Function to generate To-Do list
def generate_todo_list():
    add_button = Button(200, 250, 200, 50, "Add Task", font, (255, 255, 255), (200, 200, 200), (0, 0, 0), add_task)
    remove_button = Button(200, 320, 200, 50, "Remove Task", font, (255, 255, 255), (200, 200, 200), (0, 0, 0), remove_task)
    screen_manager.add_screen("To-Do List", Screen([todo_list, add_button, remove_button], home_button))

def add_task():
    todo_list.add_task("New task")
    generate_todo_list()  # Refresh screen after adding the task


def remove_task():
    todo_list.remove_task()
    generate_todo_list()  # Refresh screen after removing the task

# Generate the To-Do List screen when accessing it
generate_todo_list()


# Function to generate Rewards page
def generate_rewards_page():
    add_button = Button(200, 250, 200, 50, "Add Reward", font, (255, 255, 255), (200, 200, 200), (0, 0, 0), add_reward)
    remove_button = Button(200, 320, 200, 50, "Remove Reward", font, (255, 255, 255), (200, 200, 200), (0, 0, 0), remove_reward)
    screen_manager.add_screen("Rewards", Screen([rewards_list, add_button, remove_button], home_button))

def add_reward():
    rewards_list.add_task("New Reward")  # Add a new reward to the list
    generate_rewards_page()  # Refresh screen after adding the reward

def remove_reward():
    rewards_list.remove_task()  # Remove the selected reward
    generate_rewards_page()  # Refresh screen after removing the reward

# Generate the Rewards page when accessing it
generate_rewards_page()

wheel = SpinningWheel(WIDTH // 2, HEIGHT // 2, 150, rewards)

def generate_randomiser_page():
    wheel.update()
    wheel.draw(screen)
    if wheel.selected_task:
        reward_text = font.render(f"You won: {wheel.selected_task.text}", True, BLACK)
        screen.blit(reward_text, (WIDTH // 2 - reward_text.get_width() // 2, HEIGHT - 50))
    pygame.display.flip()


# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not wheel.spinning:
                wheel.start_spin()
        screen_manager.handle_event(event)  # Handle screen events
    
    screen_manager.draw(screen)

    if screen_manager.current_screen == "Randomiser":
        generate_randomiser_page()

    # Frame rate limit
    pygame.time.Clock().tick(60)

    pygame.display.flip()

pygame.quit()
