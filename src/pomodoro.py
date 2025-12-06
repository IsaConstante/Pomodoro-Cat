import webview
import threading
import time
from pathlib import Path

# Configurações do Pomodoro
pomodoro_config = {
    'work_time': 25 * 60,
    'short_break': 5 * 60,
    'long_break': 15 * 60,
    'sessions_until_long': 4
}

timer_state = {
    'running': False,
    'paused': False,
    'current_time': 25 * 60,
    'mode': 'work',
    'sessions_completed': 0
}

water_reminder = {
    'interval': 30 * 60,
    'time_remaining': 30 * 60,
}

class PomodoroAPI:
    def __init__(self):
        self.window = None
        self.timer_thread = None
        
    def set_window(self, window):
        self.window = window
    
    def start_timer(self):
        """Inicia o timer"""
        timer_state['running'] = True
        timer_state['paused'] = False
        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()
        return True
    
    def pause_timer(self):
        """Pausa/Resume o timer"""
        timer_state['paused'] = not timer_state['paused']
        return timer_state['paused']
    
    def stop_timer(self):
        """Para o timer"""
        timer_state['running'] = False
        timer_state['paused'] = False
        self.reset_timer()
        return True
    
    def reset_timer(self):
        """Reseta para o tempo inicial do modo atual"""
        mode = timer_state['mode']
        if mode == 'work':
            timer_state['current_time'] = pomodoro_config['work_time']
        elif mode == 'short_break':
            timer_state['current_time'] = pomodoro_config['short_break']
        else:
            timer_state['current_time'] = pomodoro_config['long_break']
        return timer_state['current_time']
    
    def get_config(self):
        """Retorna configurações atuais"""
        return {
            'work_minutes': pomodoro_config['work_time'] // 60,
            'short_break_minutes': pomodoro_config['short_break'] // 60,
            'long_break_minutes': pomodoro_config['long_break'] // 60,
            'sessions_until_long': pomodoro_config['sessions_until_long'],
            'water_interval_minutes': water_reminder['interval'] // 60
        }
    
    def update_config(self, work_min, short_min, long_min, sessions, water_min):
        """Atualiza configurações"""
        pomodoro_config['work_time'] = work_min * 60
        pomodoro_config['short_break'] = short_min * 60
        pomodoro_config['long_break'] = long_min * 60
        pomodoro_config['sessions_until_long'] = sessions
        water_reminder['interval'] = water_min * 60
        water_reminder['time_remaining'] = water_min * 60
        self.reset_timer()
        return True
    
    def get_timer_state(self):
        """Retorna estado atual do timer"""
        return timer_state
    
    def get_water_time(self):
        """Retorna tempo restante do lembrete de água"""
        return water_reminder['time_remaining']
    
    def run_timer(self):
        """Loop principal do timer"""
        while timer_state['running'] and timer_state['current_time'] > 0:
            if not timer_state['paused']:
                time.sleep(1)
                timer_state['current_time'] -= 1
                
                # Atualiza lembrete de água
                if water_reminder['time_remaining'] > 0:
                    water_reminder['time_remaining'] -= 1
                else:
                    self.trigger_water_reminder()
                    water_reminder['time_remaining'] = water_reminder['interval']
                
                # Atualiza interface a cada segundo
                mins = timer_state['current_time'] // 60
                secs = timer_state['current_time'] % 60
                
                if self.window:
                    self.window.evaluate_js(
                        f"update_display({mins}, {secs}, '{timer_state['mode']}')"
                    )
            else:
                time.sleep(0.1)
        
        # Timer terminou
        if timer_state['running'] and timer_state['current_time'] == 0:
            self.handle_timer_complete()
    
    def handle_timer_complete(self):
        """Lida com conclusão do timer"""
        if self.window:
            self.window.evaluate_js("play_notification_sound()")
        
        if timer_state['mode'] == 'work':
            timer_state['sessions_completed'] += 1
            
            # Verifica se é hora do intervalo longo
            if timer_state['sessions_completed'] % pomodoro_config['sessions_until_long'] == 0:
                timer_state['mode'] = 'long_break'
                timer_state['current_time'] = pomodoro_config['long_break']
                if self.window:
                    self.window.evaluate_js(
                        "show_message('Parabéns! 🎉', 'Hora do intervalo longo!')"
                    )
            else:
                timer_state['mode'] = 'short_break'
                timer_state['current_time'] = pomodoro_config['short_break']
                if self.window:
                    self.window.evaluate_js(
                        "show_message('Bom trabalho! ☕', 'Hora do intervalo!')"
                    )
        else:
            timer_state['mode'] = 'work'
            timer_state['current_time'] = pomodoro_config['work_time']
            if self.window:
                self.window.evaluate_js(
                    "show_message('Vamos lá! 💪', 'Hora de focar!')"
                )
        
        timer_state['running'] = False
        mins = timer_state['current_time'] // 60
        secs = timer_state['current_time'] % 60
        
        if self.window:
            self.window.evaluate_js(
                f"update_display({mins}, {secs}, '{timer_state['mode']}')"
            )
    
    def trigger_water_reminder(self):
        """Dispara lembrete de água"""
        if self.window:
            self.window.evaluate_js("trigger_water_reminder()")
    
    def close_window(self):
        """Fecha a janela"""
        if self.window:
            self.window.destroy()
        return True
    
    def minimize_window(self):
        """Minimiza a janela"""
        if self.window:
            self.window.minimize()
        return True


def main():
    # Cria a API
    api = PomodoroAPI()
    
    # Caminho para o HTML
    html_path = Path(__file__).parent / 'web' / 'index.html'
    
    # Cria a janela
    window = webview.create_window(
        'Pomodoro Timer 🐱',
        html_path.as_uri(),
        width=435,
        height=635,
        resizable=False,
        frameless=True,  # Remove bordas nativas
        easy_drag=True,   # Permite arrastar pela janela
        js_api=api,
        confirm_close=False  # Remove aviso ao fechar
    )
    
    # Passa a referência da janela para a API
    api.set_window(window)
    
    # Inicia o webview
    webview.start(debug=False)


if __name__ == '__main__':
    main()