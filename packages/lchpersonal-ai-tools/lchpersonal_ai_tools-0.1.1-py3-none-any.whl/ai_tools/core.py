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
    
    print(message)
    return message