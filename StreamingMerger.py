import datetime
import os
from logging import getLogger
import coloredlogs
import ffmpeg

# ログ出力の設定
logger = getLogger("Streaming Merger")
coloredlogs.install(level="INFO")

def merge_streaming_movie(url, file_name, start_num, end_num, zero_padding):
    # 引数チェック
    if type(url) is not str:
        logger.error(f"URLが不正です: {url}")
        return

    if type(file_name) is not str:
        logger.error(f"ファイル名が不正です: {file_name}")
        return

    if type(start_num) is not int or type(end_num) is not int or start_num > end_num:
        logger.error(f"開始番号と終了番号が不正です: 開始番号: {start_num}, 終了番号: {end_num}")
        return

    if type(zero_padding) is not int:
        logger.error(f"ゼロパディングの桁数が不正です: {zero_padding}")
        return

    # 開始時刻(datatime型)
    dt_start_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    start_time = dt_start_time.strftime("%Y%m%d_%H%M%S")

    # ダウンロードフォルダ設定
    download_directory = os.path.join(os.path.expanduser("~"), "Downloads")
    logger.info(f"ダウンロードディレクトリ: {download_directory}")

    # 入力動画パスリスト
    input_video_path_list = []

    for i in range(start_num, end_num + 1):
        # パディング済み番号を生成
        padding_num = str(i).zfill(zero_padding)

        # 入力動画パスを生成
        input_video_path = os.path.join(url, file_name.format(padding_num))

        # file 'URL'の形式で入力動画パスリストに追加
        input_video_path_list.append(f"file '{input_video_path}'")

        logger.info(f"URL: {input_video_path}")

    # 入力動画パスリストを一時ファイルに書き出す
    # 直接指定の場合、結合するファイル数が多い際にエラーが発生する
    temp_file_name = "tmp.txt"
    with open(temp_file_name, "w") as fp:
        fp.write("\n".join(input_video_path_list))

    # ストリーミング動画が存在する場合
    if input_video_path_list:
        # 出力動画パスを生成
        output_video_path = os.path.join(download_directory, f"output_{start_time}.mp4")

        try:
            # ffmpegで結合（再エンコードなし）
            ffmpeg.input(temp_file_name, f="concat", safe=0, protocol_whitelist="file,http,https,tls,tcp").output(output_video_path).run()
            
            # 一時ファイル削除
            os.remove(temp_file_name)

            logger.info(f"ストリーミング動画の結合が完了しました: {output_video_path}")

        except ffmpeg.Error as e:
            logger.error(f"ffmpegでエラーが発生しました: {e}")

    else:
        logger.error("ストリーミング動画が存在しないため、動画を結合せず終了します")

if __name__ == "__main__":
    url = "https://sample.com"
    file_name = "ts_{0}.ts"
    start_num = 1
    end_num = 5
    zero_padding = 5

    merge_streaming_movie(url, file_name, start_num, end_num, zero_padding)
