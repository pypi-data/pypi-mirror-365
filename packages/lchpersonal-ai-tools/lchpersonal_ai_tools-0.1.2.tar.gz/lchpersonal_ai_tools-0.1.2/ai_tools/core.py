"""
AI Tools 核心功能模块
"""


def sayHello():
    """
    输出hello world!
    
    Returns:
        str: 返回hello world!字符串
    """
    message = "hello world!"
    print(message)
    return message


def sayTest001():
    """
    显示音频特征提取代码示例
    
    Returns:
        str: 返回音频处理代码字符串
    """
    message = """
    import librosa
    import librosa.display
    import numpy as np
    import matplotlib.pyplot as plt
    import sys
    import os

    def main():
        # 1. Configuration
        audio_path = 'D:/其他/audio/30seconds.wav'  # 请确保文件路径正确
        save_img_path = 'audio_features.png'
        feature_prefix = 'features_'
        
        # 2. Verify audio file
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found at {audio_path}")
            sys.exit(1)
        
        # 3. Load audio
        try:
            audio, sr = librosa.load(audio_path, sr=16000, mono=True)
            print(f"Audio loaded: {len(audio)/sr:.2f} seconds at {sr} Hz sample rate")
        except Exception as e:
            print(f"Error loading audio: {e}")
            sys.exit(1)
        
        # 4. Feature extraction
        def extract_features(y, sr):
            # Compute STFT (Short-Time Fourier Transform)
            stft = np.abs(librosa.stft(y))
            
            # MFCC (Mel-Frequency Cepstral Coefficients)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            
            # Chroma feature
            chroma = librosa.feature.chroma_stft(S=stft, sr=sr)
            
            # Mel-scaled Spectrogram
            mel = librosa.feature.melspectrogram(y=y, sr=sr)
            mel_db = librosa.power_to_db(mel, ref=np.max)  # Convert to dB
            
            return {'stft_db': librosa.amplitude_to_db(stft, ref=np.max),
                    'mfcc': mfcc,
                    'chroma': chroma,
                    'mel_db': mel_db}

        print("Extracting audio features...")
        features = extract_features(audio, sr)
        
        # 5. Visualization setup
        plt.figure(figsize=(14, 12))
        
        # Feature 1: STFT Spectrogram
        ax1 = plt.subplot(4, 1, 1)
        stft_disp = librosa.display.specshow(features['stft_db'], 
                                            x_axis='time', 
                                            y_axis='log', 
                                            sr=sr)
        plt.title('STFT (Log Frequency)')
        plt.colorbar(format='%+2.0f dB')
        
        # Feature 2: MFCC
        plt.subplot(4, 1, 2, sharex=ax1)
        mfcc_disp = librosa.display.specshow(features['mfcc'], 
                                            x_axis='time', 
                                            sr=sr)
        plt.title('MFCC Coefficients')
        plt.colorbar()
        
        # Feature 3: Chroma
        plt.subplot(4, 1, 3, sharex=ax1)
        chroma_disp = librosa.display.specshow(features['chroma'], 
                                            x_axis='time', 
                                            y_axis='chroma', 
                                            sr=sr)
        plt.title('Chroma Features')
        plt.colorbar()
        
        # Feature 4: Mel Spectrogram
        plt.subplot(4, 1, 4, sharex=ax1)
        mel_disp = librosa.display.specshow(features['mel_db'], 
                                            x_axis='time', 
                                            y_axis='mel', 
                                            sr=sr)
        plt.title('Mel Spectrogram')
        plt.colorbar(format='%+2.0f dB')
        
        # 6. Finalize and save visualization
        plt.tight_layout()
        plt.savefig(save_img_path, dpi=300)
        print(f"Feature visualization saved to {save_img_path}")
        
        # 7. Save features as numpy arrays
        for feature_name, feature_data in features.items():
            filename = f"{feature_prefix}{feature_name}.npy"
            np.save(filename, feature_data)
            print(f"Saved {filename} ({feature_data.shape[1]} frames)")
        
        print("Feature extraction completed successfully!")

    if __name__ == "__main__":
        main()
    
    """
    
    return message


def sayTest002():
    """
    完整流程：
    1. 使用 ClearVoice speech_enhancement 模型进行语音降噪增强
    2. MOS 质量评分
    3. SRMR 清晰度评分
    """
    message = """
    from clearvoice import ClearVoice
import os
import librosa
import soundfile as sf
import numpy as np
from scipy.signal import stft


def enhance_and_score(
    input_path: str,
    output_path: str,
    se_model: str = "MossFormer2_SE_48K"
):

    # 检查输入
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"找不到输入文件: {input_path}")

    # 初始化 ClearVoice
    cv_se = ClearVoice(
        task="speech_enhancement",
        model_names=[se_model]
    )

    # 读取音频
    y, sr = librosa.load(input_path, sr=None, mono=True)

    # 根据模型后缀决定目标采样率
    target_sr = 48000 if se_model.endswith("48K") else 16000
    # 重采样到模型所需采样率
    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        sr = target_sr
        tmp_path = input_path.replace(".wav", f"_{sr//1000}k_temp.wav")
        sf.write(tmp_path, y, sr)
        model_input = tmp_path
    else:
        model_input = input_path

    # 执行语音增强，不立即写磁盘
    enhanced_audio = cv_se(
        input_path=model_input,
        online_write=False
    )

    # 保存增强结果
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv_se.write(enhanced_audio, output_path=output_path)

    # 清理临时文件
    if model_input.endswith("_temp.wav") and os.path.isfile(model_input):
        os.remove(model_input)

    # 载入增强后音频用于评分
    audio, fs = librosa.load(output_path, sr=None, mono=True)

    # 计算 MOS
    rms = librosa.feature.rms(y=audio)[0].mean()
    spectral_flatness = librosa.feature.spectral_flatness(y=audio)[0].mean()
    rms_score = min(1.5, max(0.5, rms)) * 2
    flatness_score = 4 - min(3, spectral_flatness * 5)
    mos_score = round(max(1.0, min(5.0, (rms_score + flatness_score) / 2 * 1.25)), 2)

    # 计算 SRMR（内部重采样）
    if fs > 16000:
        audio_srmr = librosa.resample(audio, orig_sr=fs, target_sr=16000)
        fs_srmr = 16000
    else:
        audio_srmr, fs_srmr = audio, fs
    f, t, Zxx = stft(audio_srmr, fs=fs_srmr, nperseg=256, noverlap=128)
    mags = np.abs(Zxx)
    speech_band = np.mean(mags[(f >= 300) & (f <= 4000)], axis=0)
    full_band = np.mean(mags, axis=0)
    srmr_score = round(max(1.0, min(10.0, np.mean(speech_band) / np.mean(full_band) * 15)), 2)

    return {
        "enhanced_path": output_path,
        "mos": mos_score,
        "srmr": srmr_score
    }


def main():
    print("=== 任务：MossFormer2_SE_48K 语音增强 + 评分 ===")

    input_audio = "D:/其他/ai_examing_002/30seconds.wav"
    output_audio = "D:/其他/ai_examing_002/30seconds-denoised.wav"

    try:
        results = enhance_and_score(input_audio, output_audio)
        print(f"✓ 增强完成，输出文件: {results['enhanced_path']}")
        print(f"✓ MOS 质量评分: {results['mos']}/5")
        print(f"✓ SRMR 清晰度评分: {results['srmr']}")
    except Exception as e:
        print(f"处理失败: {e}")


if __name__ == "__main__":
    main()

    
    """
    return message