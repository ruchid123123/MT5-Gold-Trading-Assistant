import sys
import os
import datetime
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QLabel, QPushButton, QComboBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QDialog, QStackedWidget, 
                             QGroupBox, QMessageBox, QCheckBox, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QColor, QPalette
import MetaTrader5 as mt5

# --- 线程类：处理移动止盈 (TTP) ---
class TTPThread(QThread):
    update_ui_signal = pyqtSignal(str)
    log_message_signal = pyqtSignal(str)
    fetch_positions_signal = pyqtSignal()

    def __init__(self, position_id, open_price, sl, tp1, tp2, tp3, buffer_pips, parent=None):
        super().__init__(parent)
        self.position_id = position_id
        self.open_price = open_price
        self.sl = sl
        self.tp1 = tp1
        self.tp2 = tp2
        self.tp3 = tp3
        self.buffer_pips = buffer_pips
        self.stop_flag = False
        self.current_tp_level = 1

    def run(self):
        self.log_message_signal.emit(f"已启动订单 {self.position_id} 的 TTP 监控")
        while not self.stop_flag:
            if not self.is_still_open():
                self.log_message_signal.emit(f"订单 {self.position_id} 已平仓，监控结束")
                break
            
            current_price = self.get_current_price()
            if current_price is None:
                self.msleep(1000)
                continue

            is_long = self.is_long_position()
            
            # 简单的追踪逻辑示例 (根据原版字符串推测)
            # TP1 触发 -> 移动止损到保本或 TP1 附近
            if self.current_tp_level == 1 and self.tp1 > 0:
                if (is_long and current_price >= self.tp1) or (not is_long and current_price <= self.tp1):
                    self.log_message_signal.emit(f"订单 {self.position_id} 触及 TP1: {self.tp1}")
                    self.update_stop_loss(self.open_price + (self.buffer_pips * 0.0001 if is_long else -self.buffer_pips * 0.0001))
                    self.current_tp_level = 2

            elif self.current_tp_level == 2 and self.tp2 > 0:
                if (is_long and current_price >= self.tp2) or (not is_long and current_price <= self.tp2):
                    self.log_message_signal.emit(f"订单 {self.position_id} 触及 TP2: {self.tp2}")
                    self.update_stop_loss(self.tp1)
                    self.current_tp_level = 3

            elif self.current_tp_level == 3 and self.tp3 > 0:
                if (is_long and current_price >= self.tp3) or (not is_long and current_price <= self.tp3):
                    self.log_message_signal.emit(f"订单 {self.position_id} 触及 TP3: {self.tp3}，全额平仓")
                    self.close_position()
                    break

            self.msleep(1000) # 每秒检查一次

    def is_still_open(self):
        positions = mt5.positions_get(ticket=self.position_id)
        return positions is not None and len(positions) > 0

    def is_long_position(self):
        pos = mt5.positions_get(ticket=self.position_id)
        if pos:
            return pos[0].type == mt5.ORDER_TYPE_BUY
        return True

    def get_current_price(self):
        pos = mt5.positions_get(ticket=self.position_id)
        if not pos: return None
        symbol = pos[0].symbol
        tick = mt5.symbol_info_tick(symbol)
        if not tick: return None
        return tick.bid if pos[0].type == mt5.ORDER_TYPE_BUY else tick.ask

    def update_stop_loss(self, new_sl):
        pos = mt5.positions_get(ticket=self.position_id)
        if not pos: return
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": self.position_id,
            "sl": new_sl,
            "tp": pos[0].tp,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log_message_signal.emit(f"订单 {self.position_id} 更新止损失败: {result.comment}")
        else:
            self.log_message_signal.emit(f"订单 {self.position_id} 止损已更新至 {new_sl}")
            self.fetch_positions_signal.emit()

    def close_position(self):
        pos = mt5.positions_get(ticket=self.position_id)
        if not pos: return
        symbol = pos[0].symbol
        tick = mt5.symbol_info_tick(symbol)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": self.position_id,
            "symbol": symbol,
            "volume": pos[0].volume,
            "type": mt5.ORDER_TYPE_SELL if pos[0].type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "price": tick.bid if pos[0].type == mt5.ORDER_TYPE_BUY else tick.ask,
            "deviation": 20,
            "magic": 123456,
            "comment": "TTP 自动平仓",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log_message_signal.emit(f"订单 {self.position_id} TTP 平仓失败: {result.comment}")
        else:
            self.log_message_signal.emit(f"订单 {self.position_id} TTP 平仓成功")
            self.fetch_positions_signal.emit()

    def stop(self):
        self.stop_flag = True

# --- 弹窗：部分平仓 ---
class PartialCloseModal(QDialog):
    def __init__(self, ticket, volume, parent=None):
        super().__init__(parent)
        self.ticket = ticket
        self.volume = volume
        self.setWindowTitle("部分平仓")
        layout = QVBoxLayout(self)
        
        self.label = QLabel(f"选择平仓比例 (总手数: {self.volume}):")
        layout.addWidget(self.label)
        
        self.percent_combo = QComboBox()
        self.percent_combo.addItems(["10%", "25%", "50%", "75%", "100%"])
        layout.addWidget(self.percent_combo)
        
        self.close_btn = QPushButton("确认平仓")
        self.close_btn.clicked.connect(self.on_close)
        layout.addWidget(self.close_btn)

    def on_close(self):
        percent_str = self.percent_combo.currentText().replace('%', '')
        percent = float(percent_str) / 100.0
        vol_to_close = round(self.volume * percent, 2)
        if vol_to_close < 0.01: vol_to_close = 0.01
        
        pos = mt5.positions_get(ticket=self.ticket)
        if not pos:
            QMessageBox.warning(self, "错误", "订单未找到或已关闭")
            return

        symbol = pos[0].symbol
        tick = mt5.symbol_info_tick(symbol)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": self.ticket,
            "symbol": symbol,
            "volume": vol_to_close,
            "type": mt5.ORDER_TYPE_SELL if pos[0].type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "price": tick.bid if pos[0].type == mt5.ORDER_TYPE_BUY else tick.ask,
            "deviation": 20,
            "magic": 123456,
            "comment": f"部分平仓 {percent_str}%",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            QMessageBox.information(self, "成功", f"成功平仓 {vol_to_close} 手")
            self.accept()
        else:
            QMessageBox.critical(self, "失败", f"平仓失败: {result.comment}")

# --- 弹窗：TTP 设置 ---
class TTPModal(QDialog):
    def __init__(self, ticket, open_price, sl, tp, parent=None):
        super().__init__(parent)
        self.ticket = ticket
        self.setWindowTitle(f"订单 {ticket} 的移动止盈设置")
        layout = QFormLayout(self)
        
        self.tp1_input = QLineEdit(str(tp if tp > 0 else ""))
        self.tp2_input = QLineEdit("")
        self.tp3_input = QLineEdit("")
        self.buffer_input = QLineEdit("5") # 默认 5 点缓冲
        
        layout.addRow("止盈目标 1 (TP1):", self.tp1_input)
        layout.addRow("止盈目标 2 (TP2):", self.tp2_input)
        layout.addRow("止盈目标 3 (TP3):", self.tp3_input)
        layout.addRow("缓冲点数 (Pips):", self.buffer_input)
        
        self.activate_btn = QPushButton("启动 TTP")
        self.activate_btn.clicked.connect(self.accept)
        layout.addRow(self.activate_btn)

    def get_values(self):
        try:
            return (
                float(self.tp1_input.text() or 0),
                float(self.tp2_input.text() or 0),
                float(self.tp3_input.text() or 0),
                float(self.buffer_input.text() or 0)
            )
        except:
            return 0, 0, 0, 0

# --- 主窗口 ---
class MT5TradingAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.ttp_threads = {}
        self.init_ui()
        self.init_mt5_timer()

    def init_ui(self):
        self.setWindowTitle("MT5 交易助手 - 汉化增强版")
        self.setGeometry(100, 100, 1000, 700)
        
        main_layout = QVBoxLayout(self)
        
        # 导航按钮
        nav_layout = QHBoxLayout()
        self.btn_calc = QPushButton("风险计算器")
        self.btn_manager = QPushButton("订单管理器")
        self.btn_calc.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_manager.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        nav_layout.addWidget(self.btn_calc)
        nav_layout.addWidget(self.btn_manager)
        main_layout.addLayout(nav_layout)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_calc_page())
        self.stack.addWidget(self.create_manager_page())
        main_layout.addWidget(self.stack)
        
        # 底部状态栏和控制
        bottom_layout = QHBoxLayout()
        self.btn_connect = QPushButton("连接 MT5")
        self.btn_connect.clicked.connect(self.toggle_mt5_connection)
        self.btn_log = QPushButton("显示日志")
        self.btn_log.clicked.connect(self.toggle_log)
        self.btn_theme = QPushButton("深色模式")
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        bottom_layout.addWidget(self.btn_connect)
        bottom_layout.addWidget(self.btn_log)
        bottom_layout.addWidget(self.btn_theme)
        main_layout.addLayout(bottom_layout)

        # 日志窗口
        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)
        self.log_window.setVisible(False)
        main_layout.addWidget(self.log_window)

    def create_calc_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        group = QGroupBox("黄金 (XAU/USD) 风险与仓位计算")
        form = QFormLayout(group)

        self.in_balance = QLineEdit("10000")
        self.in_risk = QLineEdit("1")
        self.in_entry = QLineEdit("")
        self.in_sl = QLineEdit("")
        self.in_tp = QLineEdit("")

        form.addRow("账户余额 ($):", self.in_balance)
        form.addRow("风险比例 (%):", self.in_risk)

        # 进场价区域
        entry_layout = QHBoxLayout()
        self.in_entry.setPlaceholderText("输入进场价或从MT5获取")
        self.btn_get_price = QPushButton("获取黄金现价")
        self.btn_get_price.clicked.connect(self.fetch_gold_price)
        entry_layout.addWidget(self.in_entry)
        entry_layout.addWidget(self.btn_get_price)
        form.addRow("进场价格:", entry_layout)

        form.addRow("止损价格:", self.in_sl)
        form.addRow("止盈价格:", self.in_tp)

        self.btn_do_calc = QPushButton("计算建议仓位")
        self.btn_do_calc.clicked.connect(self.calculate_risk)
        form.addRow(self.btn_do_calc)

        self.lbl_result = QLabel("结果将在此显示")
        self.lbl_result.setStyleSheet("font-weight: bold; color: blue;")
        form.addRow(self.lbl_result)

        layout.addWidget(group)
        layout.addStretch()
        return page

    def create_manager_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        self.acc_info = QLabel("未连接到 MT5")
        layout.addWidget(self.acc_info)
        
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "订单号", "时间", "品种", "交易量", "类型", 
            "进场价", "当前价", "止损", "盈亏", "操作"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        return page

    def init_mt5_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_data)
        self.timer.start(2000)

    def toggle_mt5_connection(self):
        if not mt5.initialize():
            self.log("MT5 初始化失败")
            return
        self.log("MT5 已连接")
        self.btn_connect.setText("已连接")
        self.update_live_data()

    def update_live_data(self):
        if not mt5.terminal_info(): return
        
        # 更新账户信息
        acc = mt5.account_info()
        if acc:
            self.acc_info.setText(f"账户: {acc.login} | 余额: {acc.balance} | 净值: {acc.equity} | 利润: {acc.profit}")
            self.in_balance.setText(str(acc.balance))
        
        # 更新持仓列表
        positions = mt5.positions_get()
        if positions is None: return
        
        self.table.setRowCount(len(positions))
        for i, pos in enumerate(positions):
            self.table.setItem(i, 0, QTableWidgetItem(str(pos.ticket)))
            self.table.setItem(i, 1, QTableWidgetItem(datetime.datetime.fromtimestamp(pos.time).strftime('%H:%M:%S')))
            self.table.setItem(i, 2, QTableWidgetItem(pos.symbol))
            self.table.setItem(i, 3, QTableWidgetItem(str(pos.volume)))
            type_str = "买入" if pos.type == mt5.ORDER_TYPE_BUY else "卖出"
            self.table.setItem(i, 4, QTableWidgetItem(type_str))
            self.table.setItem(i, 5, QTableWidgetItem(str(pos.price_open)))
            self.table.setItem(i, 6, QTableWidgetItem(str(pos.price_current)))
            self.table.setItem(i, 7, QTableWidgetItem(str(pos.sl)))
            
            profit_item = QTableWidgetItem(f"{pos.profit:.2f}")
            if pos.profit > 0:
                profit_item.setForeground(QColor("green"))
            elif pos.profit < 0:
                profit_item.setForeground(QColor("red"))
            self.table.setItem(i, 8, profit_item)
            
            # 操作按钮
            btn_layout = QHBoxLayout()
            btn_partial = QPushButton("部分平仓")
            btn_ttp = QPushButton("TTP")
            btn_partial.clicked.connect(lambda _, p=pos: self.open_partial_modal(p))
            btn_ttp.clicked.connect(lambda _, p=pos: self.open_ttp_modal(p))
            
            # 在表格中嵌入按钮
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setContentsMargins(0,0,0,0)
            cell_layout.addWidget(btn_partial)
            cell_layout.addWidget(btn_ttp)
            self.table.setCellWidget(i, 9, cell_widget)

    def fetch_gold_price(self):
        """从MT5获取黄金当前价格"""
        if not mt5.terminal_info():
            self.lbl_result.setText("错误: 请先连接MT5")
            self.lbl_result.setStyleSheet("font-weight: bold; color: red;")
            return

        symbol = "XAUUSD"
        # 尝试不同格式的黄金代码
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            symbol = "GOLD"
            tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            symbol = "XAUUSDm"
            tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            self.lbl_result.setText("错误: 无法获取黄金价格，请检查品种代码")
            self.lbl_result.setStyleSheet("font-weight: bold; color: red;")
            return

        # 使用买一价作为进场价参考
        price = tick.ask
        self.in_entry.setText(f"{price:.2f}")
        self.lbl_result.setText(f"已获取 {symbol} 价格: 买{tick.bid:.2f} / 卖{tick.ask:.2f}")
        self.lbl_result.setStyleSheet("font-weight: bold; color: green;")

    def calculate_risk(self):
        try:
            balance = float(self.in_balance.text())
            risk_pct = float(self.in_risk.text())
            entry = float(self.in_entry.text())
            sl = float(self.in_sl.text())
            tp = float(self.in_tp.text() or 0)

            if entry <= 0 or sl <= 0:
                self.lbl_result.setText("错误: 请输入有效的进场价和止损价")
                self.lbl_result.setStyleSheet("font-weight: bold; color: red;")
                return

            if entry == sl:
                self.lbl_result.setText("错误: 进场价不能等于止损价")
                self.lbl_result.setStyleSheet("font-weight: bold; color: red;")
                return

            # 黄金计算参数
            # XAU/USD: 1标准手 = 100盎司
            # 1 pip = 0.01 (价格小数点后第2位)
            # 点值 = 100 * 0.01 = $1/每pip
            oz_per_lot = 100  # 每手100盎司
            pip_size = 0.01   # 黄金1 pip = 0.01美元
            pip_value = oz_per_lot * pip_size  # $1 每pip每标准手

            # 计算风险
            risk_amt = balance * (risk_pct / 100.0)

            # 计算止损距离（点数）
            price_diff = abs(entry - sl)
            pips = price_diff / pip_size

            # 计算建议手数
            # risk_amt = lots * pips * pip_value
            # lots = risk_amt / (pips * pip_value)
            lots = risk_amt / (pips * pip_value)

            # 格式化手数（黄金通常最小0.01手）
            lots = round(lots, 2)
            if lots < 0.01:
                lots = 0.01

            # 计算潜在盈亏
            sl_pips = (entry - sl) / pip_size if entry > sl else (sl - entry) / pip_size
            sl_amount = lots * sl_pips * pip_value

            result_text = f"风险金额: ${risk_amt:.2f} | 建议手数: {lots:.2f} 手\n"
            result_text += f"止损距离: {pips:.1f} pips | 实际风险: ${sl_amount:.2f}"

            if tp > 0:
                tp_pips = (tp - entry) / pip_size if tp > entry else (entry - tp) / pip_size
                tp_amount = lots * tp_pips * pip_value
                rr_ratio = tp_pips / sl_pips if sl_pips > 0 else 0
                result_text += f"\n止盈距离: {tp_pips:.1f} pips | 潜在盈利: ${tp_amount:.2f}"
                result_text += f" | 盈亏比: 1:{rr_ratio:.1f}"

            self.lbl_result.setText(result_text)
            self.lbl_result.setStyleSheet("font-weight: bold; color: blue;")
        except ValueError as e:
            self.lbl_result.setText(f"错误: 请输入有效的数字")
            self.lbl_result.setStyleSheet("font-weight: bold; color: red;")
        except Exception as e:
            self.lbl_result.setText(f"错误: {str(e)}")
            self.lbl_result.setStyleSheet("font-weight: bold; color: red;")

    def open_partial_modal(self, pos):
        modal = PartialCloseModal(pos.ticket, pos.volume, self)
        modal.exec_()

    def open_ttp_modal(self, pos):
        modal = TTPModal(pos.ticket, pos.price_open, pos.sl, pos.tp, self)
        if modal.exec_():
            tp1, tp2, tp3, buffer = modal.get_values()
            if tp1 > 0:
                thread = TTPThread(pos.ticket, pos.price_open, pos.sl, tp1, tp2, tp3, buffer)
                thread.log_message_signal.connect(self.log)
                thread.fetch_positions_signal.connect(self.update_live_data)
                self.ttp_threads[pos.ticket] = thread
                thread.start()

    def log(self, msg):
        now = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_window.append(f"[{now}] {msg}")

    def toggle_log(self):
        self.log_window.setVisible(not self.log_window.isVisible())

    def toggle_theme(self):
        # 简化版主题切换
        if self.btn_theme.text() == "深色模式":
            self.setStyleSheet("QWidget { background-color: #2b2b2b; color: #ffffff; } QPushButton { background-color: #3c3f41; }")
            self.btn_theme.setText("浅色模式")
        else:
            self.setStyleSheet("")
            self.btn_theme.setText("深色模式")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MT5TradingAssistant()
    window.show()
    sys.exit(app.exec_())
