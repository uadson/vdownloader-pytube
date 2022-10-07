from core import (
    get_url, get_title, get_desc, 
    get_length, download_video, download_audio
)    


menu = {
    # 1: 'Informar endereço web:',
    1: 'Baixar Vídeo',
    2: 'Baixar Áudio',
    3: 'Sair'
}

resol = {
    1: '360p',
    2: '720p',
    3: '1080p',
    4: 'HQ',
}

def main():
    while True:
        while True:

            url = input('\nInforme o endereço web do vídeo que deseja baixar: ').strip()
            if not url:
                print('\nInforme um endereço web válido!')
            elif get_title(url) is None:
                print('\nEndereço inválido, tente novamente!')
            else:
                print(f'\nTítulo: {get_title(url)}')
                print(f'\nDuração: {get_length(url)}')
                print(f'\nDescrição: {get_desc(url)}')
                break

        print('\n')
        for k, v in menu.items():
            print(f"{k} - {v}")

        while True:
            try:
                opt = int(input('\nSelecione uma opção: '))
            except ValueError:
                print('Digite um número válido.')
            else:
                if opt > len(menu) or opt <= 0:
                    print('Opção inválida!')
                else:
                    break

        if opt == 1:
            print('\n')
            for k, v in resol.items():
                print(f'{k} - {v}')

            while True:
                try:
                    res = int(input('\nSelecione uma resolução: '))
                except ValueError:
                    print('Digite um número válido.')
                else:
                    if res > len(resol) or res <= 0:
                        print('Opção inválida!')
                    else:
                        break

            if res == 1:
                download_video(url, res)
                # moving_video()
                print('Vídeo baixado com sucesso!!!')
            elif res == 2:
                download_video(url, res)
                # moving_video()
                print('Vídeo baixado com sucesso!!!')
            elif res == 3:
                download_video(url, res)
                # moving_video()
                print('Vídeo baixado com sucesso!!!')

            elif res == 4:
                download_video(url, res)
                # moving_video()
                print('Vídeo baixado com sucesso!!!')

        if opt == 2:
            download_audio(url)
            print('Áudio baixado com sucesso!')

        if opt == 3:
            print('\nPrograma finalizado!')
            break

        print('\nDeseja baixar outro video/audio ?')
        try:
            answer = input('\n1 - SIM / 2 - NAO:   ' ).strip()[0]
        except ValueError:
            print('\nInforme um valor válido!')
        else:
            if int(answer) < 1 or int(answer) > 2:
                print('\nResposta incorreta.')

        if answer == '2':
            print('\nPrograma finalizado!')
            break
