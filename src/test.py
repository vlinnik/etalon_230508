import gc
print('Starting up PYPLC-230508 project!')

gc.disable()
before = gc.mem_free( )

for i in range(0,1000):
    for j in range(0,10):
        x = f'{j}'
        
print(gc.mem_free() - before)
gc.collect()
gc.enable()