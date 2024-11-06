import io

import telebot
from PIL import Image
from telebot import types

from image_designer import ImageDesigner
from image_reader import Image_reader
from nonogram_solver import NonogramSolver

TOKEN = "YOUR TOKEN HERE"


class NonogramBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.global_image_buffer = None
        self.image_buffer = None
        self.global_index = 0
        self.top_clues = []
        self.left_clues = []
        self.index_col_row = 0

        self.image_reader = Image_reader()
        self.nonogram_solver = NonogramSolver()
        self.image_designer = ImageDesigner()

        self.setup_handlers()

    def reset_values(self):
        self.global_image_buffer = None
        self.image_buffer = None
        self.global_index = 0
        self.top_clues = []
        self.left_clues = []
        self.index_col_row = 0

    def markup_yes_or_no(self):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Sim", callback_data="yes"),
            types.InlineKeyboardButton("Não", callback_data="no"),
        )

        return markup

    def markup_numbers(self):
        markup = types.InlineKeyboardMarkup(row_width=5)
        buttons_list = [
            types.InlineKeyboardButton(str(i), callback_data=str(i))
            for i in range(1, 16)
        ]
        markup.add(*buttons_list)
        markup.add(types.InlineKeyboardButton("Nenhuma", callback_data="None"))

        return markup

    def setup_handlers(self):
        @self.bot.message_handler(content_types=["photo"])
        def handle_photo(message):
            self.reset_values()
            file_id = message.photo[-1].file_id
            file_info = self.bot.get_file(file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            self.image_buffer = io.BytesIO(downloaded_file)
            self.image_buffer.seek(0)
            self.global_image_buffer = self.image_buffer

            self.bot.reply_to(
                message,
                "Imagem recebida! Estamos processando as informações, aguarde...",
            )

            image = Image.open(self.image_buffer)
            self.top_clues = self.image_reader.read_horizontal_clues(image)

            self.bot.send_message(
                message.chat.id,
                """Primeiro iremos verificar se o programa leu as dicas do jogo corretamente.

Na tabela abaixo estão todas as dicas horizontais (de cima) de seu jogo, e os números no topo da imagem são os índices de cada coluna.

Selecione "sim" caso todas as dicas estiverem corretas.

Ou "não" caso haja algum erro.""",
            )

            top_clues_pic = self.image_designer.draw_clues_horizontal(self.top_clues)
            image_buffer = io.BytesIO()
            top_clues_pic.save(image_buffer, format="JPEG")
            image_buffer.seek(0)
            final_image = self.image_designer.image_combiner_horizontal(
                self.global_image_buffer, image_buffer
            )

            markup = self.markup_yes_or_no()
            self.bot.send_photo(message.chat.id, final_image, reply_markup=markup)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            self.bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None,
            )

            if (
                call.data == "yes"
                and self.global_index == 0
                or call.data == "None"
                and self.global_index == 0
            ):
                self.bot.send_message(
                    chat_id=call.message.chat.id, text="Ótimo! Aguarde..."
                )
                self.global_index += 1

                image = Image.open(self.global_image_buffer)
                self.left_clues = self.image_reader.read_vertical_clues(image)
                left_clues_pic = self.image_designer.draw_clues_vertical(
                    self.left_clues
                )
                image_buffer = io.BytesIO()
                left_clues_pic.save(image_buffer, format="JPEG")
                image_buffer.seek(0)
                final_image = self.image_designer.image_combiner_vertical(
                    self.global_image_buffer, image_buffer
                )

                self.bot.send_message(
                    chat_id=call.message.chat.id,
                    text="""Agora iremos verificar se as dicas verticais (da esquerda) estão corretas.

Selecione "sim" caso todas as dicas estiverem corretas.

Ou "não" caso haja algum erro.""",
                )

                markup = self.markup_yes_or_no()
                self.bot.send_photo(
                    chat_id=call.message.chat.id, photo=final_image, reply_markup=markup
                )

            elif call.data == "no" and self.global_index == 0:
                markup = self.markup_numbers()
                self.bot.send_message(
                    chat_id=call.message.chat.id,
                    text="Informe o número da primeira coluna que apresente erro nas dicas:",
                    reply_markup=markup,
                )

            # Verifica se a mensagem é "sim" na verificação VERTICAL
            elif (
                call.data == "yes"
                and self.global_index == 1
                or call.data == "None"
                and self.global_index == 1
            ):
                self.bot.send_message(
                    chat_id=call.message.chat.id,
                    text="Excelente! Iremos enviar a solução do jogo agora.",
                )
                self.bot.send_message(chat_id=call.message.chat.id, text="Aguarde...")

                for item in self.left_clues:
                    self.top_clues.append(item)

                # print(self.top_clues)
                result = self.nonogram_solver.solve_puzzle(self.top_clues)
                result_pic = self.image_designer.draw_final_result(result)
                image_buffer = io.BytesIO()
                result_pic.save(image_buffer, format="JPEG")
                image_buffer.seek(0)  # Reinicie o cursor para o início do buffer

                self.bot.send_photo(chat_id=call.message.chat.id, photo=image_buffer)

            # Verifica se a mensagem é "não" na verificação VERTICAL
            elif call.data == "no" and self.global_index == 1:
                markup = self.markup_numbers()
                self.bot.send_message(
                    chat_id=call.message.chat.id,
                    text="Informe o numero da primeira linha que apresente erro nas dicas:",
                    reply_markup=markup,
                )

            # Ajustando erro nas dicas HORIZONTAIS
            elif call.data.isnumeric() and self.global_index == 0:
                self.index_col_row = call.data
                self.bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"""Envie uma mensagem com as dicas corretas da coluna {call.data} separadas por virugula.

Exemplo: 1, 2, 1""",
                )

            # Ajustando erro nas dicas VERTICAIS
            elif call.data.isnumeric() and self.global_index == 1:
                self.index_col_row = call.data
                self.bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"""Envie uma mensagem com as dicas corretas da linha {call.data} separadas por virugula.

Exemplo: 1, 2, 1""",
                )

        @self.bot.message_handler(func=lambda message: True)
        def handle_text_message(message):
            items = [item.strip() for item in message.text.split(",")]

            if all(item.isnumeric() for item in items) and self.global_index == 0:
                items = [int(item) for item in items]
                self.top_clues[int(self.index_col_row) - 1] = items

                top_clues_pic = self.image_designer.draw_clues_horizontal(
                    self.top_clues
                )
                image_buffer = io.BytesIO()
                top_clues_pic.save(image_buffer, format="JPEG")
                image_buffer.seek(0)
                final_image = self.image_designer.image_combiner_horizontal(
                    self.global_image_buffer, image_buffer
                )

                self.bot.send_message(
                    message.chat.id, text="Todas as dicas estão corretas agora?"
                )
                markup = self.markup_yes_or_no()
                self.bot.send_photo(message.chat.id, final_image, reply_markup=markup)

            # Corrije as dicas VERTICAIS e reenvia a imagem para validação
            elif all(item.isnumeric() for item in items) and self.global_index == 1:
                items = [int(item) for item in items]
                self.left_clues[int(self.index_col_row) - 1] = items

                left_clues_pic = self.image_designer.draw_clues_vertical(
                    self.left_clues
                )
                image_buffer = io.BytesIO()
                left_clues_pic.save(image_buffer, format="JPEG")
                image_buffer.seek(0)  # Reinicie o cursor para o início do buffer
                final_image = self.image_designer.image_combiner_vertical(
                    self.global_image_buffer, image_buffer
                )

                self.bot.send_message(
                    message.chat.id, text="Todas as dicas estão corretas agora?"
                )
                markup = self.markup_yes_or_no()
                self.bot.send_photo(message.chat.id, final_image, reply_markup=markup)

            else:
                self.bot.send_message(
                    message.chat.id,
                    text="Mensagem invalida! Verifique as informações e tente novamente.",
                )

    def start(self):
        self.bot.polling()


if __name__ == "__main__":
    bot = NonogramBot(TOKEN)
    bot.start()
