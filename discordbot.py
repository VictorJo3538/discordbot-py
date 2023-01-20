import asyncio
from nextcord.ext import commands
from nextcord import Interaction, FFmpegPCMAudio
import nextcord
from youtube_dl import YoutubeDL
import bs4
from selenium import webdriver
import chromedriver_autoinstaller
import time
import os

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix='.')
music_pl_ch = 1048652105180782633

YDL_OPTIONS = {'format': 'bestaudio', 'yesplaylist': 'True',
               'quiet': True,
               }
FFMPEG_OPTIONS = {
    'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class Button(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(emoji="▶️", style=nextcord.ButtonStyle.grey)
    async def play(self, button: nextcord.ui.Button, interaction: Interaction):
        global vc, song_queue, info_dic
        try:
            if not vc.is_playing():
                vc.resume()
                url = song_queue[0]
                info = info_dic[url]
                title = info['title']
                URL = info['formats'][0]['url']
                # 임베드 만들기
                embed = nextcord.Embed(
                    title="재생 중인 노래 다운",
                    url=URL,
                    description=f"현재 재생중인 노래입니다\n"
                                f"[{title}]\n"
                                f"{url}",
                    color=0x6CAAD0)
                embed.set_author(
                    name='음악 재생중',
                    icon_url=
                    'https://cdn-icons-png.flaticon.com/512/1941/1941064.png')
                thumbnail_url = info['thumbnail']
                embed.set_image(url=thumbnail_url)
                await display.edit(embed=embed)
        except:
            pass

    @nextcord.ui.button(emoji="⏸️", style=nextcord.ButtonStyle.grey)
    async def pause(self, button: nextcord.ui.Button,
                    interaction: Interaction):
        global vc, song_queue, info_dic, display
        try:
            if vc.is_playing():
                vc.pause()
                url = song_queue[0]
                info = info_dic[url]
                title = info['title']
                embed = nextcord.Embed(
                    title="'▶' 버튼을 눌러 다시 재생시킬 수 있습니다.",
                    description=f"[{title}]\n"
                                f"{url}",
                    color=0xFFB400)
                embed.set_author(
                    name='현재 노래 재생 멈춤',
                    url=url,
                    icon_url=
                    'https://cdn-icons-png.flaticon.com/512/1941/1941064.png')
                thumbnail_url = info['thumbnail']
                embed.set_image(url=thumbnail_url)
                await display.edit(embed=embed)
        except:
            pass

    @nextcord.ui.button(emoji="⏭️", style=nextcord.ButtonStyle.grey)
    async def next(self, button: nextcord.ui.Button, interaction: Interaction):
        global vc
        if vc.is_playing():
            vc.pause()

        play_next()

    @nextcord.ui.button(emoji="⏹️", style=nextcord.ButtonStyle.grey)
    async def stop(self, button: nextcord.ui.Button, interaction: Interaction):
        global song_queue, info_dic, display, displayQ
        song_queue.clear()
        info_dic.clear()
        try:
            await vc.disconnect()
            embed = nextcord.Embed(
                description="노래의 주소를 채팅창에 넣거나\n'.검색 노래제목' 을 통해 검색해 주세요.",
                color=0x6CAAD0)
            embed.set_author(
                name='음악이 재생중이 아님',
                icon_url=
                'https://cdn-icons-png.flaticon.com/512/1941/1941064.png')
            embed.set_image(
                url="https://media.tenor.com/5FmfYNNPcwQAAAAC/dance-music.gif")
            await display.edit(embed=embed)
            await displayQ.edit(embed=nextcord.Embed(
                title='대기열', description='현재 대기열에 곡 없음', color=0xC71585))
        except:
            pass

    @nextcord.ui.button(label="help", style=nextcord.ButtonStyle.red)
    async def help(self, button: nextcord.ui.Button, interaction: Interaction, help_message=None):
        embed = nextcord.Embed(
            description="⚠️모든 기능은 통화 채널에 입장 후 정상작동합니다⚠️\n"
                        "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ\n"
                        "'▶' 버튼은 일시 정지된 음악을 다시재생 합니다.\n"
                        "️'⏸️' 버튼은 음악을 일시 정지 합니다.\n"
                        "'⏭️' 버튼은 대기열의 다음 음악을 재생시킵니다.\n"
                        "'⏹' 버튼은 재생중인 음악을 종료시키고, 대기열을 삭제합니다.\n"
                        "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ\n"
                        "특정 대기열을 삭제하려면 [.삭제 {번호}] 또는 [.삭제 {번호}~{번호}] 를 이용해주세요\n"
                        "ㅤㅤex) .삭제 1, .삭제 1~12\n"
                        "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ\n"
                        "음악을 검색하려면 [.검색 {검색어}] 를 이용해주세요\n"
                        "ㅤㅤex) .검색 대한민국 애국가\n"
                        "ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ\n"
                        "로그인 된 유튜브에서 링크로 붙여넣은 대기열은\n"
                        "실제 음악 봇에서 재생되는 노래 대기열과 상이할 수 있습니다.",
            color=0x66F8F0)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.ui.button(label="restart", style=nextcord.ButtonStyle.green)
    async def restart(self, button: nextcord.ui.Button, interaction: Interaction):
        try:
            await on_ready()
        except:
            pass


@bot.listen("on_ready")
async def on_ready():
    global song_queue, info_dic
    song_queue = []  # url이 들어있다.
    info_dic = {}
    # 메시지 있으면 삭제
    try:
        await bot.get_channel(music_pl_ch).purge()
    finally:
        pass
    channel = bot.get_channel(music_pl_ch)
    print(f'{bot.user.name} 작동완료')
    await bot.change_presence(status=nextcord.Status.online,
                              activity=nextcord.Game("탈영 생각"))
    embed = nextcord.Embed(
        description="노래의 주소를 채팅창에 넣거나\n'.검색 노래제목' 을 통해 검색해 주세요.",
        color=0x6CAAD0)
    embed.set_author(
        name='음악이 재생중이 아님',
        icon_url='https://cdn-icons-png.flaticon.com/512/1941/1941064.png')
    embed.set_image(
        url="https://media.tenor.com/5FmfYNNPcwQAAAAC/dance-music.gif")

    global display
    display = await channel.send(embed=embed)

    view = Button()
    await channel.send(view=view)

    global displayQ
    displayQ = await channel.send(embed=nextcord.Embed(
        title='대기열', description='현재 대기열에 곡 없음', color=0xC71585))


@bot.listen('on_message')
async def on_message(msg):
    # 음악재생
    if msg.channel.id == music_pl_ch:
        # 봇이 대답한것 생략
        if msg.author == bot.user:
            return
        else:
            await msg.delete()
        if msg.content.startswith("http"):
            await startMusic(author=msg.author, link=msg.content)


async def startMusic(author, link):
    try:
        await connectVoice(author)
    except nextcord.errors.ClientException as e:
        print(e)
        await addQueue(url=link, channel=bot.get_channel(music_pl_ch))
        await playMusic()
    except AttributeError as e:
        print(e)
        embed = nextcord.Embed(title="⚠️주의⚠️",
                               description=f"음성채널에 들어오세요",
                               color=0xC71585)
        await warning(embed)
    else:
        await addQueue(url=link, channel=bot.get_channel(music_pl_ch))
        await playMusic()


async def playMusic():
    global display, FFMPEG_OPTIONS
    embed, URL = playnow()
    await display.edit(embed=embed)
    await showQueue()
    if not vc.is_playing():
        try:
            vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS),
                    after=lambda a: play_next())
        except Exception as e:
            print(e)
            play_next()


def play_next():
    global vc, song_queue, info_dic, YDL_OPTIONS, FFMPEG_OPTIONS, display
    # 이미 재생한 노래를 목록에서 삭제
    try:
        delQueue(0)
    except:
        pass
    if not vc.is_playing():
        try:
            if len(song_queue) >= 1:
                embed, URL = playnow()
                bot.loop.create_task(display.edit(embed=embed))
                bot.loop.create_task(showQueue())
                vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS),
                        after=lambda a: play_next())
        except Exception as e:
            print(e)
            play_next()
        if len(song_queue) == 0:
            time.sleep(30)
            bot.loop.create_task(vc.disconnect())
            return


# def disconnect_delay

def playnow():
    global song_queue, info_dic
    url = song_queue[0]
    info = info_dic[url]
    URL = info['formats'][0]['url']
    title = info['title']
    embed = nextcord.Embed(
        title="재생 중인 노래 다운",
        url=URL,
        description=f"현재 재생중인 노래입니다\n"
                    f"[{title}]\n"
                    f"{url}",
        color=0x6CAAD0)
    embed.set_author(
        name='음악 재생중',
        icon_url='https://cdn-icons-png.flaticon.com/512/1941/1941064.png')
    thumbnail_url = info['thumbnail']
    embed.set_image(url=thumbnail_url)
    return embed, URL


async def connectVoice(author):
    global vc
    print("vc생성")
    vc = await author.voice.channel.connect()


async def showQueue():
    global song_queue, info_dic, displayQ
    title_list = []
    title_queue = []
    if len(song_queue) >= 2:
        for url in song_queue:  # song_queue 에서 url을 가져와서
            info = info_dic[url]  # info 객체를 받아온다
            title_list.append(
                info['title'])  # info 객체에서 title을 뽑아 title_list에 넣는다

        length = len(title_list)
        for i in range(1, length):
            title_queue.append(
                f'{i}. {title_list[i]}\n')  # 'index. 노래제목' 이렇게 나오게 큐로 저장

        await displayQ.edit(embed=nextcord.Embed(
            title='대기열', description=''.join(title_queue), color=0xC71585))
    elif len(song_queue) <= 1:
        await displayQ.edit(embed=nextcord.Embed(
            title='대기열', description='현재 대기열에 곡 없음', color=0xC71585))


async def addQueue(url, channel):
    global song_queue, info_dic, YDL_OPTIONS
    if '&list=' in url:
        warn = await channel.send(embed=nextcord.Embed(
            title='플레이스트 등록중. 시간이 오래 걸립니다...', color=0xC71585))
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
    if 'entries' in info:
        await warn.delete()
        for obj in info['entries']:
            url = obj['webpage_url']
            song_queue.append(url)  # 큐에 url 추가
            info_dic[url] = obj  # info_dic 딕셔너리에 {url: info} 형태로 저장
    else:
        song_queue.append(url)  # 큐에 url 추가
        info_dic[url] = info  # info_dic 딕셔너리에 {url: info} 형태로 저장


bot.get_channel(music_pl_ch)


def delQueue(num):
    global song_queue, info_dic
    del info_dic[song_queue[num]]
    del song_queue[num]


async def warning(msg):
    try:
        warn = await bot.get_channel(music_pl_ch).send(embed=msg)
        await asyncio.sleep(3)
        await warn.delete()
    except Exception as e:
        print(e)


@bot.command()
async def 검색(ctx, *msg):
    # 검색어 다듬기
    search_query = msg[0]
    for i in range(1, len(msg)):
        search_query += f"+{msg[i]}"
    print(search_query)
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("headless")
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.youtube.com/results?search_query=" + search_query)
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'})
    entireNum = entire[0]
    musicurl = entireNum.get('href')
    url = 'https://www.youtube.com' + musicurl
    driver.quit()
    await startMusic(author=ctx.author, link=url)


@bot.command()
async def 삭제(ctx, *, msg):
    global song_queue, info_dic
    if '~' in msg:
        index = msg
        index = index.split('~')
        n1 = int(index[0])
        n2 = int(index[1])
        if n1 < n2:
            for i in range(n1, n2 + 1):
                del info_dic[song_queue[n1]]
                del song_queue[n1]
        elif n1 > n2:
            for i in range(n2, n1 + 1):
                del info_dic[song_queue[n2]]
                del song_queue[n2]
        elif n1 == n2:
            warn = await ctx.send(
                embed=nextcord.Embed(
                    description='한 개의 대기열을 삭제할 때는 "삭제 (대기열 번호)" 를 이용해 주세요',
                    color=0xC71585))
            await asyncio.sleep(3)
            await warn.delete()

        await showQueue()
    else:
        index = int(msg)
        del info_dic[song_queue[index]]
        del song_queue[index]
        await showQueue()


def start():
  try:
      bot.run(os.environ['TOKEN'])
  except:
    pass


start()
