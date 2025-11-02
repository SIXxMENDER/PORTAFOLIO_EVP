import pandas as pd
import numpy as np
import sys
EXPECTED_PROFIT_FACTOR = 1.21
EXPECTED_SHARPE_RATIO = 1.49
EXPECTED_MIN_TRADES = 90
EXPECTED_MAX_DRAWDOWN_PERCENT = 13.0 # %

def analyze_trades(csv_file, initial_balance=10000):

    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {csv_file}")
        sys.exit(1)

    if df.empty:
        print("Error: El archivo de trades está vacío.")
        sys.exit(1)

    total_trades = len(df)
    gross_profit = df[df['profit'] > 0]['profit'].sum()
    gross_loss = abs(df[df['profit'] < 0]['profit'].sum())
    
    if gross_loss == 0:
        profit_factor = float('inf') # Caso de 100% victorias
    else:
        profit_factor = gross_profit / gross_loss

    df['equity'] = initial_balance + df['profit'].cumsum()
    df['drawdown'] = df['equity'] / df['equity'].cummax() - 1.0
    max_drawdown_percent = abs(df['drawdown'].min() * 100)
    
    returns = df['profit'] / initial_balance
    if returns.std() == 0:
        sharpe_ratio = float('inf')
    else:
        # Anualizar: (Retorno Promedio / Desv. Estándar) * sqrt(N)
        # N es trades por año. (99 trades / 2 años) ~ 50.
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(total_trades / 2.0)

    print("--- INICIANDO PROTOCOLO DE VALIDACIÓN V5 ---")
    print(f"Trades Totales: {total_trades}")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Sharpe Ratio (aprox.): {sharpe_ratio:.2f}")
    print(f"Máximo Drawdown: {max_drawdown_percent:.2f}%")

    try:
        assert total_trades >= EXPECTED_MIN_TRADES
        print(f"✓ PRUEBA DE FRECUENCIA: {total_trades} >= {EXPECTED_MIN_TRADES} (PASSED)")
        
        assert profit_factor > 1.0
        print(f"✓ PRUEBA DE RENTABILIDAD: {profit_factor:.2f} > 1.0 (PASSED)")
        
        assert sharpe_ratio > 1.0
        print(f"✓ PRUEBA DE SHARPE: {sharpe_ratio:.2f} > 1.0 (PASSED)")
        
        assert max_drawdown_percent < EXPECTED_MAX_DRAWDOWN_PERCENT
        print(f"✓ PRUEBA DE SOBERANÍA (DD): {max_drawdown_percent:.2f}% < {EXPECTED_MAX_DRAWDOWN_PERCENT}% (PASSED)")
        
        print("\n--- VALIDACIÓN DE RIGOR COMPLETADA (v5.2) ✓ ---")

    except AssertionError as e:
        print(f"\n--- ✗ FALLO DE VALIDACIÓN DE RIGOR ---")
        if total_trades < EXPECTED_MIN_TRADES:
            print(f"Falla de Frecuencia: {total_trades} < {EXPECTED_MIN_TRADES}")
        if profit_factor <= 1.0:
            print(f"Falla de Rentabilidad: {profit_factor:.2f} <= 1.0")
        if sharpe_ratio <= 1.0:
            print(f"Falla de Sharpe: {sharpe_ratio:.2f} <= 1.0")
        if max_drawdown_percent >= EXPECTED_MAX_DRAWDOWN_PERCENT:
            print(f"Falla de Soberanía (DD): {max_drawdown_percent:.2f}% >= {EXPECTED_MAX_DRAWDOWN_PERCENT}%")
        sys.exit(1)

if __name__ == "__main__":
    analyze_trades("trades.csv")
