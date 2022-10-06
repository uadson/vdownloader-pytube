from core import (
    get_url, get_title, get_desc, 
    download, moving_video
)    


menu = {
    1: 'Informar endereço web:',
    2: 'Mostrar Título e Descrição',
    3: 'Baixar Vídeo',
    4: 'Baixar Áudio',
    5: 'Sair'
}

# '360p': 18
# '720p': 22
# '1080p': 137
# 'HQ': 0

resol = {
    1: '360p',
    2: '720p',
    3: '1080p',
    4: 'HQ',
}

def main():
    while True:
        print('\n')
        for k, v in menu.items():
            print(f"{k} - {v}")
        
        opt = int(input('\nSelecione uma opção: '))
        
        if opt == 1:
            try: 
                url = input('\nInforme o endereço web do vídeo que deseja baixar: ').strip()
                if not url:
                    print('\nInforme um endereço web válido!')
                elif get_title(url) is None:
                    print('\nEndereço inválido, tente novamente!')
            except KeyboardInterrupt:
                print('\nPrograma finalizado!')
                break

        if opt == 2:
            print(f'\nTítulo: {get_title(url)}')
            print(f'Descrição: {get_desc(url)}')

        if opt == 3:
            print('\n')
            for k, v in resol.items():
                print(f'{k} - {v}')
            res = int(input('\nSelecione uma resolução: '))

            if res == 1:
                download(url, 18, resol)
                moving_video()
                print('Vídeo baixado com sucesso!!!')
            elif res == 2:
                download(url, 22, resol)
                moving_video()
                print('Vídeo baixado com sucesso!!!')
            elif res == 3:
                download(url, 137, resol)
                moving_video()
                print('Vídeo baixado com sucesso!!!')

            elif res == 4:
                download(url, res, resol)
                moving_video()
                print('Vídeo baixado com sucesso!!!')

        if opt == 5:
            print('\nPrograma finalizado!')
            break
